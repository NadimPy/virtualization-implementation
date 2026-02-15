# Infrastructure Setup Guide

This document provides complete step-by-step instructions to set up the VM Provisioner from scratch using **Ansible automation** with SSL/HTTPS enabled by default.

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
- Domain pointing to server's IP: `beirut-central1.nadimchendy.com`

---

## Quick Start

### Deploy with Ansible (SSL/HTTPS enabled by default)
```bash
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation
nano ansible/inventory.ini  # Add your server IP
bash ansible/setup.sh
```

That's it! 🎉 The playbook will:
- ✅ Install all system dependencies
- ✅ Set up libvirt/KVM
- ✅ Deploy the application
- ✅ Install and configure Nginx with SSL
- ✅ Get SSL certificate from Let's Encrypt
- ✅ Start the service with HTTPS at https://beirut-central1.nadimchendy.com

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
enable_ssl=true
domain=beirut-central1.nadimchendy.com
```

#### 2. Run the Playbook
```bash
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
```

Or use the setup script:
```bash
bash ansible/setup.sh
```

### What the Playbook Does

| Step | Task |
|------|------|
| 1 | Updates apt cache |
| 2 | Installs system packages (libvirt, qemu, nginx, certbot) |
| 3 | Creates service user (`vmprovisioner`) |
| 4 | Creates data directories |
| 5 | Copies application files |
| 6 | Sets up Python virtual environment with uv |
| 7 | Installs Python dependencies |
| 8 | Creates systemd service |
| 9 | Configures iptables for port forwarding |
| 10 | Configures Nginx with SSL proxy |
| 11 | Gets SSL certificate from Let's Encrypt |
| 12 | Downloads Debian 12 base image |
| 13 | Starts the service |

---

## Verification

### Check Service Status
```bash
systemctl status vm-provisioner
systemctl status nginx
```

### Test API
```bash
curl https://beirut-central1.nadimchendy.com/health
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
apt install -y qemu-kvm libvirt-daemon-system nginx certbot

# 2. Clone and setup
cd /opt
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation

# Initialize uv project
uv init
uv add fastapi uvicorn pycdlib jinja2 python-dotenv libvirt-python

# Create directories
mkdir -p /var/lib/vm-provisioner/{images,instances,cloud-init}
chmod -R 777 /var/lib/vm-provisioner
cp .env.example .env

# 3. Configure SSL with certbot
certbot --nginx -d beirut-central1.nadimchendy.com

# 4. Run with uvicorn (behind nginx proxy)
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*
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
dig beirut-central1.nadimchendy.com

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
