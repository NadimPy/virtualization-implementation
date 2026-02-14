# Infrastructure Setup Guide

This document provides complete step-by-step instructions to set up the VM Provisioner from scratch using **Ansible automation** - including SSL/HTTPS!

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Ansible Automation](#ansible-automation)
4. [Verification](#verification)
5. [Manual Setup (Alternative)](#manual-setup-alternative)

---

## Prerequisites

### Local Machine (Ansible Control Node)
- Ansible 2.14+
- SSH access to target server

### Target Server
- Ubuntu 22.04 LTS or Debian 12
- Root or sudo access via SSH
- At least 8GB RAM, 100GB storage
- CPU with virtualization support (Intel VT-x/AMD-V)
- **For SSL**: A domain name pointing to your server's IP

---

## Quick Start

### Deploy without SSL (HTTP only)
```bash
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation
nano ansible/inventory.ini  # Add your server IP
bash ansible/setup.sh
```

### Deploy WITH SSL (HTTPS)
```bash
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation
nano ansible/inventory.ini  # Add your server IP

# Run with SSL - just add your domain!
bash ansible/setup.sh --ssl vm.yourdomain.com
```

That's it! 🎉 The playbook will:
- ✅ Install all system dependencies
- ✅ Set up libvirt/KVM
- ✅ Deploy the application
- ✅ Install and configure Nginx
- ✅ Get SSL certificate from Let's Encrypt
- ✅ Start the service with HTTPS

---

## Ansible Automation

### Configuration

#### 1. Edit Inventory
```bash
nano ansible/inventory.ini
```

```ini
[vm_provisioner]
192.168.1.100 ansible_user=root ansible_python_interpreter=/usr/bin/python3

[vm_provisioner:vars]
app_dir=/opt/vm-provisioner
data_dir=/var/lib/vm-provisioner
```

#### 2. Run the Playbook

**Without SSL:**
```bash
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
```

**With SSL (automated):**
```bash
# Option A: Via setup.sh
bash ansible/setup.sh --ssl vm.yourdomain.com

# Option B: Direct ansible command
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml \
  -e "enable_ssl=true domain=vm.yourdomain.com"
```

### What the Playbook Does

| Step | Task |
|------|------|
| 1 | Updates apt cache |
| 2 | Installs system packages (libvirt, qemu, python, nginx, certbot) |
| 3 | Creates service user (`vmprovisioner`) |
| 4 | Creates data directories |
| 5 | Copies application files |
| 6 | Sets up Python virtual environment |
| 7 | Installs Python dependencies |
| 8 | Creates systemd service |
| 9 | Configures iptables for port forwarding |
| 10 | Configures Nginx with SSL proxy |
| 11 | Gets SSL certificate from Let's Encrypt |
| 12 | Downloads Debian 12 base image |
| 13 | Starts the service |

### SSL Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `enable_ssl` | Enable SSL/HTTPS | `false` |
| `domain` | Your domain name | `""` |
| `app_port` | Backend port | `8000` |

Example with custom port:
```bash
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml \
  -e "enable_ssl=true domain=vm.example.com app_port=8080"
```

---

## Verification

### Check Service Status
```bash
systemctl status vm-provisioner
systemctl status nginx
```

### Test API
```bash
# With SSL
curl https://vm.yourdomain.com/health

# Without SSL
curl http://your-server-ip:8000/health
```

### Check Logs
```bash
journalctl -u vm-provisioner -f
```

---

## Manual Setup (Alternative)

If you prefer manual setup without Ansible:

```bash
# 1. Install dependencies
apt update
apt install -y qemu-kvm libvirt-daemon-system nginx certbot python3-venv

# 2. Clone and setup
cd /opt
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation

python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pycdlib jinja2 python-dotenv libvirt-python

mkdir -p /var/lib/vm-provisioner/{images,instances,cloud-init}
chmod -R 777 /var/lib/vm-provisioner
cp .env.example .env

# 3. Run
python main.py &

# 4. Setup Nginx with SSL
certbot --nginx -d your-domain.com
```

---

## Troubleshooting

### Ansible Connection Issues
```bash
# Test SSH connection
ssh root@your-server-ip

# Ping hosts
ansible -i ansible/inventory.ini all -m ping
```

### Certbot SSL Issues
```bash
# Check if domain points to correct IP
dig your-domain.com

# Check nginx error logs
tail -f /var/log/nginx/error.log

# Renew certificate manually
certbot renew
```

### Service Failed to Start
```bash
journalctl -u vm-provisioner -n 50
systemctl status libvirtd
virsh list --all
```
