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
    Add iptables rules to forward host_port -> vm_ip:22.
    
    This allows: ssh -p <host_port> user@<server_public_ip>
    
    Three rules are needed:
      1. PREROUTING DNAT: rewrite destination to vm_ip:22
      2. FORWARD ACCEPT: allow the rewritten packet through to the VM
         (inserted at top of chain so it comes before libvirt's REJECT rules)
      3. POSTROUTING MASQUERADE: source-NAT so VM reply traffic routes back
         through the host correctly
    """
    # DNAT rule in PREROUTING
    dnat_cmd = [
        "iptables", "-t", "nat", "-A", "PREROUTING",
        "-p", "tcp",
        "--dport", str(host_port),
        "-j", "DNAT",
        "--to-destination", f"{vm_ip}:22"
    ]
    subprocess.run(dnat_cmd, check=True, capture_output=True, text=True)
    
    # FORWARD rule — use -I (insert at top) instead of -A (append) so it is
    # evaluated before libvirt's default REJECT rules for the virbr0 bridge.
    forward_cmd = [
        "iptables", "-I", "FORWARD",
        "-p", "tcp",
        "-d", vm_ip,
        "--dport", "22",
        "-m", "conntrack", "--ctstate", "NEW,ESTABLISHED,RELATED",
        "-j", "ACCEPT"
    ]
    subprocess.run(forward_cmd, check=True, capture_output=True, text=True)
    
    # MASQUERADE rule so that DNAT'd traffic arriving at the VM appears to come
    # from the host bridge IP.  This guarantees reply packets route back through
    # the host where conntrack can reverse the DNAT.
    masq_cmd = [
        "iptables", "-t", "nat", "-A", "POSTROUTING",
        "-p", "tcp",
        "-d", vm_ip,
        "--dport", "22",
        "-j", "MASQUERADE"
    ]
    subprocess.run(masq_cmd, check=True, capture_output=True, text=True)
    
    logger.info(f"Added port forward: host:{host_port} -> {vm_ip}:22")


def remove_port_forward(host_port: int, vm_ip: str) -> None:
    """Remove iptables DNAT, FORWARD, and MASQUERADE rules when VM is destroyed."""
    # Remove DNAT rule
    dnat_cmd = [
        "iptables", "-t", "nat", "-D", "PREROUTING",
        "-p", "tcp",
        "--dport", str(host_port),
        "-j", "DNAT",
        "--to-destination", f"{vm_ip}:22"
    ]
    subprocess.run(dnat_cmd, check=False, capture_output=True, text=True)
    
    # Remove FORWARD rule (matches the -I rule we added)
    forward_cmd = [
        "iptables", "-D", "FORWARD",
        "-p", "tcp",
        "-d", vm_ip,
        "--dport", "22",
        "-m", "conntrack", "--ctstate", "NEW,ESTABLISHED,RELATED",
        "-j", "ACCEPT"
    ]
    subprocess.run(forward_cmd, check=False, capture_output=True, text=True)
    
    # Remove MASQUERADE rule
    masq_cmd = [
        "iptables", "-t", "nat", "-D", "POSTROUTING",
        "-p", "tcp",
        "-d", vm_ip,
        "--dport", "22",
        "-j", "MASQUERADE"
    ]
    subprocess.run(masq_cmd, check=False, capture_output=True, text=True)
    
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


def _suppress_libvirt_errors():
    """
    Install a no-op libvirt error handler to suppress stderr spam.
    
    The default libvirt error handler prints messages like
    'libvirt: QEMU Driver error : Guest agent is not responding'
    directly to stderr every time a guest-agent query fails.
    Replacing the handler silences this while we still catch the
    libvirtError exception in Python.
    """
    def _noop_error_handler(_userdata, _error):
        pass
    
    libvirt.registerErrorHandler(_noop_error_handler, None)


def _restore_libvirt_errors():
    """Restore the default libvirt error handler."""
    libvirt.registerErrorHandler(None, None)


def poll_vm_ip(libvirt_conn, vm_uuid: str, timeout: int = 120) -> str:
    """
    Poll for VM IP address using multiple methods.
    
    Strategy:
      - Wait a few seconds for the VM to boot before polling.
      - Primarily use DHCP leases (works without a guest agent).
      - Try the guest agent only after an initial grace period.
      - Fall back to reading dnsmasq leases file on disk.
    
    Args:
        libvirt_conn: libvirt connection object
        vm_uuid: Libvirt UUID string
        timeout: Seconds to wait for IP (default raised to 120 for
                 slower-booting images like Rocky Linux)
    
    Returns:
        VM's internal IP address (e.g., 192.168.122.45)
    
    Raises:
        TimeoutError: If IP not available within timeout
    """
    dom = libvirt_conn.lookupByUUIDString(vm_uuid)
    mac_address = None
    poll_interval = 2
    max_attempts = timeout // poll_interval
    
    # Seconds before we start trying the guest agent (let cloud-init install it)
    agent_grace_seconds = 30
    
    # Suppress libvirt's default stderr error handler so guest-agent failures
    # don't flood the journal with 'Guest agent is not responding' messages.
    _suppress_libvirt_errors()
    
    try:
        for attempt in range(max_attempts):
            elapsed = attempt * poll_interval
            
            # Method 1: DHCP leases via libvirt API (most reliable, no agent needed)
            try:
                ifaces = dom.interfaceAddresses(
                    libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE
                )
                for iface_name, iface_data in ifaces.items():
                    if mac_address is None and iface_data.get("hwaddr"):
                        mac_address = iface_data["hwaddr"]
                    for addr in iface_data.get("addrs", []):
                        ip = addr.get("addr")
                        if ip and not ip.startswith("127."):
                            logger.info(f"Found IP {ip} for VM {vm_uuid} via DHCP lease")
                            return ip
            except libvirt.libvirtError:
                pass
            
            # Method 2: QEMU guest agent — only try after the grace period
            # so we don't spam errors while cloud-init is still installing it.
            if elapsed >= agent_grace_seconds:
                try:
                    ifaces = dom.interfaceAddresses(
                        libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT
                    )
                    for iface_name, iface_data in ifaces.items():
                        for addr in iface_data.get("addrs", []):
                            if addr.get("type") == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                ip = addr.get("addr")
                                if ip and not ip.startswith("127."):
                                    logger.info(
                                        f"Found IP {ip} for VM {vm_uuid} via guest agent"
                                    )
                                    return ip
                except libvirt.libvirtError:
                    pass
            
            # Log progress every 10 seconds instead of spamming every 2s
            if elapsed > 0 and elapsed % 10 == 0:
                logger.info(
                    f"Waiting for IP for VM {vm_uuid}... ({elapsed}s/{timeout}s)"
                )
            
            time.sleep(poll_interval)
        
        # Method 3: Fall back to reading dnsmasq leases file directly
        if mac_address:
            ip = get_vm_ip_from_leases(mac_address, timeout=15)
            if ip:
                logger.info(f"Found IP {ip} for VM {vm_uuid} via leases file")
                return ip
        
        raise TimeoutError(f"Could not get IP for VM {vm_uuid} within {timeout}s")
    
    finally:
        # Always restore the default error handler so other libvirt operations
        # still report errors normally.
        _restore_libvirt_errors()


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