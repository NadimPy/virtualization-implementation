import subprocess
import time
import logging
import json
import libvirt
from pathlib import Path

from config import START_PORT, END_PORT, VM_NETWORK
from SQL.database import get_conn

logger = logging.getLogger(__name__)


def allocate_port() -> int:
    """
    Find next available host port for SSH forwarding.
    Scans database to find highest used port, returns next.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT MAX(host_port) FROM vms"
        ).fetchone()
        
        max_port = row[0] if row[0] else START_PORT - 1
        next_port = max_port + 1
        
        if next_port > END_PORT:
            raise RuntimeError(f"No available ports in range {START_PORT}-{END_PORT}")
        
        return next_port


def add_port_forward(host_port: int, vm_ip: str) -> None:
    """
    Add iptables DNAT rule to forward host_port -> vm_ip:22.
    
    This allows: ssh -p <host_port> user@<server_public_ip>
    """
    cmd = [
        "iptables", "-t", "nat", "-A", "PREROUTING",
        "-p", "tcp",
        "--dport", str(host_port),
        "-j", "DNAT",
        "--to-destination", f"{vm_ip}:22"
    ]
    
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    logger.info(f"Added port forward: host:{host_port} -> {vm_ip}:22")


def remove_port_forward(host_port: int, vm_ip: str) -> None:
    """Remove iptables DNAT rule when VM is destroyed."""
    cmd = [
        "iptables", "-t", "nat", "-D", "PREROUTING",
        "-p", "tcp",
        "--dport", str(host_port),
        "-j", "DNAT",
        "--to-destination", f"{vm_ip}:22"
    ]
    
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    logger.info(f"Removed port forward: host:{host_port} -> {vm_ip}:22")


def get_vm_ip_from_leases(mac_address: str, timeout: int = 30) -> str | None:
    """
    Get VM IP from libvirt's dnsmasq leases file.
    Fallback if qemu-guest-agent fails.
    """
    leases_file = Path(f"/var/lib/libvirt/dnsmasq/{VM_NETWORK}.leases")
    
    for _ in range(timeout):
        if leases_file.exists():
            content = leases_file.read_text()
            for line in content.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 5 and parts[1].lower() == mac_address.lower():
                    return parts[2]  # IP address
        
        time.sleep(1)
    
    return None


def poll_vm_ip(libvirt_conn, vm_uuid: str, timeout: int = 60) -> str:
    """
    Poll qemu-guest-agent for VM IP address.
    
    Args:
        libvirt_conn: libvirt connection object
        vm_uuid: Libvirt UUID string
        timeout: Seconds to wait for IP
    
    Returns:
        VM's internal IP address (e.g., 192.168.122.45)
    
    Raises:
        TimeoutError: If IP not available within timeout
    """
    dom = libvirt_conn.lookupByUUIDString(vm_uuid)
    
    for attempt in range(timeout // 2):
        try:
            # Query guest agent for network interfaces
            result = dom.guestInfo(
                libvirt.VIR_DOMAIN_GUEST_INFO_INTERFACES,
                0  # flags
            )
            
            # Parse result (JSON string from agent)
            if result:
                interfaces = json.loads(result)
                for iface in interfaces.get("interfaces", []):
                    if iface.get("name") == "eth0" or iface.get("name") == "enp1s0":
                        for addr in iface.get("addresses", []):
                            if addr.get("type") == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                ip = addr.get("addr")
                                if ip and not ip.startswith("127."):
                                    logger.info(f"Found IP {ip} for VM {vm_uuid}")
                                    return ip
        
        except libvirt.libvirtError:
            # Guest agent not ready yet
            pass
        
        time.sleep(2)
    
    raise TimeoutError(f"Could not get IP for VM {vm_uuid} within {timeout}s")


def generate_mac_address(vm_id: str) -> str:
    """
    Generate deterministic MAC address from VM UUID.
    Ensures same VM always gets same MAC (helps with DHCP consistency).
    """
    import hashlib
    hash_bytes = hashlib.sha256(vm_id.encode()).digest()
    # Libvirt MAC prefix 52:54:00 is for KVM
    mac = f"52:54:00:{hash_bytes[0]:02x}:{hash_bytes[1]:02x}:{hash_bytes[2]:02x}"
    return mac