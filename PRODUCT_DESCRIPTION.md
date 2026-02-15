# VM Provisioner - Product Descriptions

## 1. Short Tagline (GitHub Subtitle)

> Self-hosted VM provisioning API with KVM/Libvirt - provision VMs on demand with cloud-init

---

## 2. Medium Description (GitHub Main Description)

A self-hosted VM provisioning service that mimics cloud provider APIs. Built with FastAPI and Libvirt/KVM, it allows you to create and manage virtual machines through a REST API. Features include automatic SSH key injection via cloud-init, port forwarding, copy-on-write disk images, one-click Ansible deployment, and SSL/HTTPS enabled by default.

---

## 3. Full Product Page Content

```markdown
# VM Provisioner 🖥️☁️

**Self-hosted VM provisioning API - provision virtual machines on demand**

VM Provisioner is a REST API that lets you create and manage KVM virtual machines programmatically. Think of it as a self-hosted alternative to AWS EC2 or Google Compute Engine.

## 🚀 Features

- **REST API** - Create, list, and delete VMs via HTTP endpoints
- **Cloud-init** - Automatic SSH key injection and cloud config
- **Port Forwarding** - Automatic NAT configuration for VM access
- **Copy-on-write Disks** - Fast VM provisioning with disk images
- **Ansible Automation** - One-command server deployment
- **SSL/HTTPS** - Automatic Let's Encrypt integration (enabled by default)
- **Multi-image Support** - Debian, Rocky Linux, Alpine, and more
- **API Authentication** - Secure API key-based access

## ⚡ Quick Start

```bash
# Deploy with Ansible (SSL/HTTPS enabled by default!)
bash ansible/setup.sh

# Or manually with uv
git clone https://github.com/your-repo/virtualization-implementation.git
cd virtualization-implementation
uv init
uv add fastapi uvicorn pycdlib jinja2 python-dotenv libvirt-python
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Example

```bash
# Create a VM
curl -X POST "https://beirut-central1.nadimchendy.com/vms" \
  -H "X-API-Key: your-key" \
  -d '{
    "name": "my-server",
    "ssh_key": "ssh-rsa AAAAB3...",
    "image_type": "debian-12",
    "memory_mb": 1024,
    "vcpus": 2
  }'
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Virtualization**: Libvirt/KVM
- **VM Init**: Cloud-init
- **Database**: SQLite
- **Automation**: Ansible
- **Package Manager**: uv
- **Reverse Proxy**: Nginx + Let's Encrypt

## 📋 Requirements

- Linux server with KVM support
- Ubuntu 22.04 or Debian 12
- 8GB+ RAM, 100GB+ storage
- Domain pointing to server

## 🔐 Use Cases

- Development environments
- Self-hosted cloud services
- CI/CD runners
- Teaching/learning virtualization
- Private cloud infrastructure
```

---

## 4. GitHub Topics/Tags

```
virtualization kvm libvirt cloud-init vm-provisioner fastapi self-hosted 
devops infrastructure-as-code ansible rest-api linux cloud-computing
```

---

## 5. Badges

```markdown
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)
[![Ansible](https://img.shields.io/badge/Ansible-2.14+-red.svg)](https://ansible.com)
[![SSL](https://img.shields.io/badge/SSL-Enabled-brightgreen)](https://letsencrypt.org)
```
