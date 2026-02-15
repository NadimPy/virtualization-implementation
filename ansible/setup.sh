#!/bin/bash
# VM Provisioner - Ansible Setup Script
#
# Usage:
#   bash ansible/setup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}VM Provisioner - Ansible Setup${NC}\n"

# Check if ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${YELLOW}Ansible not found. Installing...${NC}"
    
    # Try pipx first (recommended for Debian 12)
    if ! command -v pipx &> /dev/null; then
        echo "Installing pipx..."
        apt-get update && apt-get install -y pipx
    fi
    
    # Install ansible via pipx
    pipx install ansible-core
    pipx ensurepath
    
    # Source the path
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install ansible collections
echo -e "${YELLOW}Installing Ansible collections...${NC}"
~/.local/bin/ansible-galaxy collection install community.general ansible.posix

# Check inventory file
if [ ! -f "ansible/inventory.ini" ]; then
    echo -e "${RED}Error: ansible/inventory.ini not found${NC}"
    echo "Please edit ansible/inventory.ini and add your server details"
    exit 1
fi

# Check if server is configured in inventory
if grep -q "your-server-ip" ansible/inventory.ini; then
    echo -e "${YELLOW}Warning: Please configure your server in ansible/inventory.ini${NC}"
    echo "Edit the file and replace 'your-server-ip' with your server IP or hostname"
    exit 1
fi

echo -e "${BLUE}SSL/HTTPS is enabled by default${NC}"
echo -e "Domain: beirut-central1.nadimchendy.com"
echo ""

# Run the playbook (use full path)
echo -e "${GREEN}Running Ansible playbook...${NC}\n"
~/.local/bin/ansible-playbook -i ansible/inventory.ini ansible/playbook.yml

echo -e "\n${GREEN}=========================================="
echo "Setup complete!"
echo "==========================================${NC}"

echo -e "🌐 HTTPS: https://beirut-central1.nadimchendy.com"
echo ""
echo "To check service status: systemctl status vm-provisioner"
echo "To view logs: journalctl -u vm-provisioner -f"
echo "To restart: systemctl restart vm-provisioner"
