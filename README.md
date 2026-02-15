# Virtualization-implementation

## About The Project

EC2 and Google Compute Engine are fascinating cloud services, this project tries to imitate these services to provision VMs from known Linux images on demand. It consists mainly of a FastAPI backend that uses libvirt to interface with KVM to provision VMs on demand.

## Features

* 🚀 Create/delete VMs on demand
* 🔑 SSH key injection via cloud-init
* 🌐 Automatic port allocation and NAT forwarding
* 💾 Copy-on-write disk images
* 📊 RESTful API
* 🔒 SSL/HTTPS enabled by default
* 🐳 Docker support
* ⚙️ Ansible automation for one-click server provisioning

## Quick Start

``` Please note that the domain is HARDCODED to my domain beirut-central1.nadimchendy.com please change it to yours ```

### Ansible Automation

```bash
# 1. Clone repository
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation

# 2. Configure server IP
nano ansible/inventory.ini

# 3. Deploy (SSL/HTTPS enabled by default)
bash ansible/setup.sh
```

That's it! The Ansible playbook automatically:
- Installs all system dependencies
- Sets up libvirt/KVM
- Deploys the application
- Configures Nginx with SSL
- Gets SSL certificate from Let's Encrypt
- Starts the service with HTTPS

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/vms` | Create a new VM |
| `GET` | `/vms` | List all VMs |
| `GET` | `/vms/{vm_id}` | Get VM details |
| `DELETE` | `/vms/{vm_id}` | Delete a VM |
| `GET` | `/images` | List available VM images |
| `GET` | `/health` | Health check |

### Example: Create a VM

```bash
curl -X POST "https://beirut-central1.nadimchendy.com/vms" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "my-vm",
    "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB...",
    "image_type": "debian-12",
    "memory_mb": 1024,
    "vcpus": 2
  }'
```

## Configuration

Edit `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATA_DIR` | Base data directory | `/var/lib/vm-provisioner` |
| `DB_PATH` | SQLite database path | `{DATA_DIR}/vms.db` |
| `LIBVIRT_URI` | Libvirt connection URI | `qemu:///system` |
| `START_PORT` | Port range start | `2222` |
| `END_PORT` | Port range end | `2322` |

## Ansible Automation

The project includes full automation in [`ansible/`](ansible) directory:

| File | Description |
|------|-------------|
| [`ansible/playbook.yml`](ansible/playbook.yml) | Main provisioning playbook |
| [`ansible/inventory.ini`](ansible/inventory.ini) | Server inventory |
| [`ansible/setup.sh`](ansible/setup.sh) | Setup script |
| [`ansible/requirements.yml`](ansible/requirements.yml) | Ansible dependencies |

SSL/HTTPS is enabled by default. The domain is ==HARDCODED== in the inventory file.

## Testing

```bash
uv add --dev pytest pytest-asyncio
uv run pytest tests/ -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
