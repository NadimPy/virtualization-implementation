import io
import pycdlib
import jinja2
from pathlib import Path
import tempfile
import os
from config import CLOUD_INIT_DIR, CLOUD_INIT_ISO_LABEL, TEMPLATE_DIR, IMAGES

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=True,
    lstrip_blocks=True
)

def render_template(template_name: str, variables: dict) -> str:
    """Render a Jinja2 template with given variables."""
    template = env.get_template(template_name)
    return template.render(**variables)

def create_config_iso(vm_id: str, name: str, image_type: str, ssh_key: str,
                      mac_address: str = "") -> Path:
    """
    Generate cloud-init ISO for a VM.
    
    Args:
        vm_id: UUID of the VM
        name: Hostname for the VM
        image_type: Key from IMAGES dict (debian-12, rocky-9, alpine)
        ssh_key: SSH public key to inject
        mac_address: MAC address of the VM's network interface
    
    Returns:
        Path to generated ISO file
    """
    # Get username from image config
    username = IMAGES[image_type]["username"]
    
    # Render YAML files
    user_data = render_template("user-data.yaml.j2", {
        "name": name,
        "username": username,
        "ssh_key": ssh_key
    })
    
    meta_data = render_template("meta-data.yaml.j2", {
        "vm_id": vm_id,
        "name": name
    })
    
    network_config = render_template("network-config.yaml.j2", {
        "mac_address": mac_address,
    })
    
    # Ensure output directory exists
    CLOUD_INIT_DIR.mkdir(parents=True, exist_ok=True)
    iso_path = CLOUD_INIT_DIR / f"{vm_id}.iso"
    
    # Create ISO with pycdlib
    iso = pycdlib.PyCdlib()
    iso.new(
        interchange_level=3,
        vol_ident=CLOUD_INIT_ISO_LABEL,
        joliet=True,
        rock_ridge='1.09'
    )
    
    # Add user-data file
    user_data_bytes = user_data.encode('utf-8')
    iso.add_fp(
        io.BytesIO(user_data_bytes),
        len(user_data_bytes),
        '/USER_DATA;1',
        joliet_path='/user-data',
        rr_name='user-data'
    )
    
    # Add meta-data file
    meta_data_bytes = meta_data.encode('utf-8')
    iso.add_fp(
        io.BytesIO(meta_data_bytes),
        len(meta_data_bytes),
        '/META_DATA;1',
        joliet_path='/meta-data',
        rr_name='meta-data'
    )
    
    # Add network-config file
    # Required by RHEL-based images (Rocky Linux, CentOS) to enable DHCP.
    # Without this, the VM may boot without network and never get a DHCP lease.
    network_config_bytes = network_config.encode('utf-8')
    iso.add_fp(
        io.BytesIO(network_config_bytes),
        len(network_config_bytes),
        '/NETWORK_C.;1',
        joliet_path='/network-config',
        rr_name='network-config'
    )
    
    # Write and close
    iso.write(str(iso_path))
    iso.close()
    
    return iso_path

def delete_config_iso(vm_id: str) -> None:
    """Remove cloud-init ISO after VM is created (optional cleanup)."""
    iso_path = CLOUD_INIT_DIR / f"{vm_id}.iso"
    if iso_path.exists():
        iso_path.unlink()