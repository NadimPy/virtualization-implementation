import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.getenv("DATA_DIR", "/var/lib/vm-provisioner"))

# Subdirectories
IMAGE_DIR = DATA_DIR / "images"
INSTANCE_DIR = DATA_DIR / "instances"
CLOUD_INIT_DIR = DATA_DIR / "cloud-init"
TEMPLATE_DIR = BASE_DIR / "templates"

# Database
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "vms.db"))

# Libvirt
LIBVIRT_URI = os.getenv("LIBVIRT_URI", "qemu:///system")

# VM Defaults
DEFAULT_MEMORY_MB = int(os.getenv("DEFAULT_MEMORY_MB", "512"))
DEFAULT_VCPUS = int(os.getenv("DEFAULT_VCPUS", "1"))
DEFAULT_DISK_GB = int(os.getenv("DEFAULT_DISK_GB", "10"))

# VM Resource Limits
MIN_MEMORY_MB = int(os.getenv("MIN_MEMORY_MB", "10"))
MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", "10"))
MIN_VCPUS = int(os.getenv("MIN_VCPUS", "10"))
MAX_VCPUS = int(os.getenv("MAX_VCPUS", "10"))

# Network
START_PORT = int(os.getenv("START_PORT", "2222"))
END_PORT = int(os.getenv("END_PORT", "2322"))
VM_NETWORK = os.getenv("VM_NETWORK", "default")  # libvirt network name

# Available images
IMAGES = {
    "debian-12": {
        "name": "Debian 12 (Bookworm)",
        "template_path": IMAGE_DIR / "debian-12-template.qcow2",
        "username": "debian"
    },
    "rocky-9": {
        "name": "Rocky Linux 9",
        "template_path": IMAGE_DIR / "rocky-9-template.qcow2",
        "username": "rocky"
    },
    "alpine": {
        "name": "Alpine Linux",
        "template_path": IMAGE_DIR / "alpine-template.qcow2",
        "username": "alpine"
    }
}

# Cloud-init
CLOUD_INIT_ISO_LABEL = "cidata"

def ensure_directories():
    """Create all required directories."""
    for path in [DATA_DIR, IMAGE_DIR, INSTANCE_DIR, CLOUD_INIT_DIR]:
        path.mkdir(parents=True, exist_ok=True)