import subprocess
from pathlib import Path
import logging

from config import INSTANCE_DIR, IMAGES

logger = logging.getLogger(__name__)


def clone_base_image(vm_id: str, image_type: str) -> Path:
    """
    Create copy-on-write clone of template image.
    
    Args:
        vm_id: UUID for the new VM
        image_type: Key from IMAGES dict (debian-12, rocky-9, alpine)
    
    Returns:
        Path to cloned disk image
    """
    template_path = IMAGES[image_type]["template_path"]
    dest_path = INSTANCE_DIR / f"{vm_id}.qcow2"
    
    # Ensure instance directory exists
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Verify template exists
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    # Create copy-on-write clone (backing file)
    cmd = [
        "qemu-img", "create",
        "-f", "qcow2",
        "-F", "qcow2",
        "-b", str(template_path),
        str(dest_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    logger.info(f"Created clone {dest_path} from {template_path}")
    
    return dest_path


def delete_disk_image(vm_id: str) -> None:
    """Remove VM disk image."""
    disk_path = INSTANCE_DIR / f"{vm_id}.qcow2"
    if disk_path.exists():
        disk_path.unlink()
        logger.info(f"Deleted disk {disk_path}")


def get_disk_info(vm_id: str) -> dict:
    """Get qcow2 image info (size, backing file, etc)."""
    disk_path = INSTANCE_DIR / f"{vm_id}.qcow2"
    
    if not disk_path.exists():
        raise FileNotFoundError(f"Disk not found: {disk_path}")
    
    result = subprocess.run(
        ["qemu-img", "info", "--output=json", str(disk_path)],
        capture_output=True,
        text=True,
        check=True
    )
    
    import json
    return json.loads(result.stdout)


def resize_disk(vm_id: str, new_size_gb: int) -> None:
    """
    Resize VM disk. Must be done while VM is stopped.
    Size is in GB, converted to qemu-img format (e.g., '20G').
    """
    disk_path = INSTANCE_DIR / f"{vm_id}.qcow2"
    
    cmd = ["qemu-img", "resize", str(disk_path), f"{new_size_gb}G"]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    logger.info(f"Resized {disk_path} to {new_size_gb}GB")