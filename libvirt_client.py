import libvirt
import logging
import jinja2
from pathlib import Path

from config import LIBVIRT_URI, TEMPLATE_DIR, VM_NETWORK, DEFAULT_MEMORY_MB, DEFAULT_VCPUS
from network import generate_mac_address

logger = logging.getLogger(__name__)

# Global connection cache
_conn = None

# Jinja2 for XML rendering
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=True,
    lstrip_blocks=True
)


def get_conn() -> libvirt.virConnect:
    """Get or create libvirt connection."""
    global _conn
    if _conn is None or not _conn.isAlive():
        _conn = libvirt.open(LIBVIRT_URI)
        logger.info(f"Connected to libvirt at {LIBVIRT_URI}")
    return _conn


def build_domain_xml(
    vm_id: str,
    name: str,
    disk_path: Path,
    iso_path: Path,
    memory_mb: int = DEFAULT_MEMORY_MB,
    vcpus: int = DEFAULT_VCPUS
) -> str:
    """
    Render domain XML from template.
    
    Args:
        vm_id: UUID for the VM
        name: Hostname
        disk_path: Path to qcow2 disk
        iso_path: Path to cloud-init ISO
        memory_mb: RAM in megabytes
        vcpus: Number of virtual CPUs
    
    Returns:
        Complete XML string for libvirt
    """
    template = env.get_template("domain.xml.j2")
    
    # Generate MAC from VM ID (deterministic)
    mac_address = generate_mac_address(vm_id)
    
    # Convert MB to KB for libvirt
    memory_kb = memory_mb * 1024
    
    xml = template.render(
        name=name,
        vm_id=vm_id,
        memory_kb=memory_kb,
        vcpus=vcpus,
        disk_path=str(disk_path),
        iso_path=str(iso_path),
        network=VM_NETWORK,
        mac_address=mac_address
    )
    
    return xml


def create_domain(xml: str) -> str:
    """
    Define and start a new VM.
    
    Args:
        xml: Complete domain XML
    
    Returns:
        Libvirt UUID string
    """
    conn = get_conn()
    
    # Define (persistent) but don't start yet
    dom = conn.defineXML(xml)
    
    if dom is None:
        raise RuntimeError("Failed to define domain")
    
    # Start the VM
    dom.create()
    
    uuid = dom.UUIDString()
    logger.info(f"Created and started VM {uuid}")
    
    return uuid


def destroy_domain(vm_uuid: str, undefine: bool = True) -> None:
    """
    Stop and optionally undefine a VM.
    
    Args:
        vm_uuid: Libvirt UUID
        undefine: If True, remove persistent definition
    """
    conn = get_conn()
    dom = conn.lookupByUUIDString(vm_uuid)
    
    if dom.isActive():
        dom.destroy()
        logger.info(f"Destroyed running VM {vm_uuid}")
    
    if undefine:
        dom.undefine()
        logger.info(f"Undefined VM {vm_uuid}")


def get_domain_state(vm_uuid: str) -> str:
    """
    Get VM state as string.
    
    Returns: 'running', 'paused', 'shutoff', etc.
    """
    conn = get_conn()
    dom = conn.lookupByUUIDString(vm_uuid)
    
    state, _ = dom.state()
    states = {
        libvirt.VIR_DOMAIN_NOSTATE: 'nostate',
        libvirt.VIR_DOMAIN_RUNNING: 'running',
        libvirt.VIR_DOMAIN_BLOCKED: 'blocked',
        libvirt.VIR_DOMAIN_PAUSED: 'paused',
        libvirt.VIR_DOMAIN_SHUTDOWN: 'shutdown',
        libvirt.VIR_DOMAIN_SHUTOFF: 'shutoff',
        libvirt.VIR_DOMAIN_CRASHED: 'crashed',
        libvirt.VIR_DOMAIN_PMSUSPENDED: 'suspended'
    }
    return states.get(state, 'unknown')


def list_all_domains() -> list[dict]:
    """List all domains (for admin/debug)."""
    conn = get_conn()
    domains = []
    
    for dom in conn.listAllDomains():
        domains.append({
            'uuid': dom.UUIDString(),
            'name': dom.name(),
            'state': get_domain_state(dom.UUIDString())
        })
    
    return domains