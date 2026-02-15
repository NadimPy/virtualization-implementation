import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import (
    ensure_directories, 
    IMAGES, 
    MIN_MEMORY_MB, 
    MAX_MEMORY_MB, 
    MIN_VCPUS, 
    MAX_VCPUS
)
from SQL.database import init_db
from SQL.USERS_related import get_user_by_api_key
from SQL.VM_related import (
    add_vm_record, 
    get_vm_by_id, 
    list_vms_by_owner, 
    delete_vm_record,
    VMRecord
)
from libvirt_client import (
    create_domain, 
    build_domain_xml, 
    destroy_domain, 
    get_domain_state,
    get_conn as get_libvirt_conn
)
from storage import clone_base_image, delete_disk_image
from cloudinit import create_config_iso, delete_config_iso
from network import (
    allocate_port, 
    add_port_forward, 
    remove_port_forward,
    poll_vm_ip
)

import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_directories()
    init_db()
    logger.info("VM Provisioner started")
    yield
    logger.info("VM Provisioner shutting down")


app = FastAPI(title="VM Provisioner", lifespan=lifespan)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the dashboard frontend."""
    from pathlib import Path
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    return FileResponse(frontend_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_current_user(x_api_key: str = Header(..., alias="X-API-Key")):
    user = get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(401, "Invalid API key")
    return user


def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def cleanup_vm_resources(vm_id: str, host_port: int | None, vm_ip: str | None, 
                        disk_path: str | None, iso_path: str | None, 
                        libvirt_uuid: str | None):
    """Best-effort cleanup on failure."""
    logger.info(f"Cleaning up resources for failed VM {vm_id}")
    
    if host_port and vm_ip:
        try:
            remove_port_forward(host_port, vm_ip)
        except Exception as e:
            logger.warning(f"Cleanup: failed to remove port forward: {e}")
    
    if libvirt_uuid:
        try:
            destroy_domain(libvirt_uuid, undefine=True)
        except Exception as e:
            logger.warning(f"Cleanup: failed to destroy domain: {e}")
    
    if disk_path:
        try:
            delete_disk_image(vm_id)
        except Exception as e:
            logger.warning(f"Cleanup: failed to delete disk: {e}")
    
    if iso_path:
        try:
            delete_config_iso(vm_id)
        except Exception as e:
            logger.warning(f"Cleanup: failed to delete ISO: {e}")


@app.post("/vms")
async def create_vm(
    name: str,
    ssh_key: str,
    image_type: str = "debian-12",
    memory_mb: int = 512,
    vcpus: int = 1,
    user: dict = Depends(get_current_user)
):
    """
    Create a new VM.
    """
    # Validate inputs
    if image_type not in IMAGES:
        raise HTTPException(400, f"Unknown image type: {image_type}")
    
    memory_mb = clamp(memory_mb, MIN_MEMORY_MB, MAX_MEMORY_MB)
    vcpus = clamp(vcpus, MIN_VCPUS, MAX_VCPUS)
    
    vm_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Variables for cleanup tracking
    host_port = None
    disk_path = None
    iso_path = None
    libvirt_uuid = None
    vm_ip = None
    
    try:
        # 1. Allocate port
        host_port = allocate_port()
        
        # 2. Create cloud-init ISO
        iso_path = str(create_config_iso(vm_id, name, image_type, ssh_key))
        
        # 3. Clone disk image (blocking IO, run in thread)
        loop = asyncio.get_event_loop()
        disk_path = str(await loop.run_in_executor(
            None, clone_base_image, vm_id, image_type
        ))
        
        # 4. Build XML and create VM
        xml = build_domain_xml(
            vm_id=vm_id,
            name=name,
            disk_path=disk_path,
            iso_path=iso_path,
            memory_mb=memory_mb,
            vcpus=vcpus
        )
        libvirt_uuid = await loop.run_in_executor(None, create_domain, xml)
        
        # 5. Poll for IP (blocking, has internal timeout)
        conn = get_libvirt_conn()
        vm_ip = await loop.run_in_executor(None, poll_vm_ip, conn, libvirt_uuid)
        
        # 6. Setup port forward
        await loop.run_in_executor(None, add_port_forward, host_port, vm_ip)
        
        # 7. Save to DB
        vm_record: VMRecord = {
            "id": vm_id,
            "name": name,
            "owner_id": user["id"],
            "status": "running",
            "ip": vm_ip,
            "host_port": host_port,
            "disk_path": disk_path,
            "iso_path": iso_path,
            "created_at": now
        }
        await loop.run_in_executor(None, add_vm_record, vm_record)
        
        # 8. Return success
        server_ip = os.getenv("SERVER_PUBLIC_IP", "127.0.0.1")
        username = IMAGES[image_type]["username"]
        
        return {
            "id": vm_id,
            "name": name,
            "status": "running",
            "ssh_connection": {
                "host": server_ip,
                "port": host_port,
                "username": username,
                "command": f"ssh -p {host_port} {username}@{server_ip}"
            },
            "specs": {
                "memory_mb": memory_mb,
                "vcpus": vcpus,
                "image": IMAGES[image_type]["name"]
            }
        }
        
    except Exception as e:
        logger.error(f"VM creation failed: {e}")
        cleanup_vm_resources(vm_id, host_port, vm_ip, disk_path, iso_path, libvirt_uuid)
        raise HTTPException(500, f"VM creation failed: {str(e)}")


@app.get("/vms")
def list_vms(user: dict = Depends(get_current_user)):
    """List all VMs for current user."""
    vms = list_vms_by_owner(user["id"])
    
    result = []
    for vm in vms:
        try:
            status = get_domain_state(vm["id"])
        except Exception as e:
            status = "unknown"
        
        result.append({
            "id": vm["id"],
            "name": vm["name"],
            "status": status,
            "ip": vm.get("ip"),
            "port": vm["host_port"],
            "created_at": vm["created_at"]
        })
    
    return {"vms": result}


@app.get("/vms/{vm_id}")
def get_vm(vm_id: str, user: dict = Depends(get_current_user)):
    """Get specific VM details."""
    vm = get_vm_by_id(vm_id, user["id"])
    if not vm:
        raise HTTPException(404, "VM not found")
    
    server_ip = os.getenv("SERVER_PUBLIC_IP", "127.0.0.1")
    
    # Determine username from iso_path or store image_type in DB
    username = "debian"  # Default, should parse from stored data
    
    return {
        "id": vm["id"],
        "name": vm["name"],
        "status": get_domain_state(vm["id"]),
        "ssh_connection": {
            "host": server_ip,
            "port": vm["host_port"],
            "username": username,
            "command": f"ssh -p {vm['host_port']} {username}@{server_ip}"
        },
        "created_at": vm["created_at"]
    }


@app.delete("/vms/{vm_id}")
def delete_vm(vm_id: str, user: dict = Depends(get_current_user)):
    """Destroy a VM and cleanup resources."""
    vm = get_vm_by_id(vm_id, user["id"])
    if not vm:
        raise HTTPException(404, "VM not found")
    
    # Remove port forward
    try:
        remove_port_forward(vm["host_port"], vm["ip"])
    except Exception as e:
        logger.warning(f"Failed to remove port forward: {e}")
    
    # Stop and undefine in libvirt
    try:
        destroy_domain(vm_id, undefine=True)
    except Exception as e:
        logger.warning(f"Failed to destroy domain: {e}")
    
    # Cleanup files
    delete_disk_image(vm_id)
    delete_config_iso(vm_id)
    
    # Remove from DB
    delete_vm_record(vm_id, user["id"])
    
    return {"deleted": True, "id": vm_id}


@app.get("/images")
def list_images():
    """List available VM images."""
    return {
        key: {"name": val["name"], "username": val["username"]}
        for key, val in IMAGES.items()
    }


@app.post("/auth/signup")
async def signup(name: str, password: str):
    """
    Register a new user. Returns the API key (shown only once).
    """
    import secrets
    
    # Generate a secure API key
    api_key = secrets.token_urlsafe(32)
    
    # Add user to database
    from SQL.USERS_related import add_user
    user = add_user(name, password, api_key)
    
    if user is None:
        raise HTTPException(400, "User already exists or invalid data")
    
    return {
        "message": "User created successfully",
        "api_key": api_key,
        "user_id": user["id"]
    }


@app.post("/auth/login")
async def login(name: str, password: str):
    """
    Login with username and password. Returns the API key if valid.
    """
    from SQL.USERS_related import verify_password
    from SQL.database import get_conn
    
    # Get user by name
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, hashed_password, api_key_hash FROM users WHERE name = ?",
            (name,)
        ).fetchone()
    
    if not row:
        raise HTTPException(401, "Invalid username or password")
    
    user = dict(row)
    
    # Verify password
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(401, "Invalid username or password")
    
    # Get the plaintext API key (we need to store it or have a way to retrieve it)
    # For now, let's regenerate a new API key on login
    import secrets
    new_api_key = secrets.token_urlsafe(32)
    
    # Update the API key in database
    from SQL.USERS_related import hash_api_key
    new_hash = hash_api_key(new_api_key)
    
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET api_key_hash = ? WHERE id = ?",
            (new_hash, user["id"])
        )
        conn.commit()
    
    return {
        "message": "Login successful",
        "api_key": new_api_key,
        "user_id": user["id"],
        "name": user["name"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)