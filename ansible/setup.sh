#!/bin/bash
# VM Provisioner - Ansible Setup Script
#
# Usage:
#   Basic:     bash ansible/setup.sh
#   With SSL:  bash ansible/setup.sh --ssl vm.example.com

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}VM Provisioner - Ansible Setup${NC}\n"

# Parse arguments
ENABLE_SSL=false
DOMAIN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --ssl)
            ENABLE_SSL=true
            DOMAIN="$2"
            shift 2
            ;;
        --ssl-only)
            ENABLE_SSL=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--ssl <domain>]"
            exit 1
            ;;
    esac
done

# Check if ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${YELLOW}Ansible not found. Installing...${NC}"
    pip install -r ansible/requirements.yml
fi

# Check inventory file
if [ ! -f "ansible/inventory.ini" ]; then
    echo -e "${RED}Error: ansible/inventory.ini not found${NC}"
    echo "Please edit ansible/inventory.ini and add your server details"
    exit 1
fi

# Check if server is configured in inventory
if grep -q "example.com" ansible/inventory.ini; then
    echo -e "${YELLOW}Warning: Please configure your server in ansible/inventory.ini${NC}"
    echo "Edit the file and replace 'example.com' with your server IP or hostname"
    exit 1
fi

# Build extra vars
EXTRA_VARS=""
if [ "$ENABLE_SSL" = true ]; then
    if [ -z "$DOMAIN" ]; then
        echo -e "${RED}Error: Domain required for SSL${NC}"
        echo "Usage: $0 --ssl vm.example.com"
        exit 1
    fi
    echo -e "${BLUE}SSL enabled for domain: $DOMAIN${NC}\n"
    EXTRA_VARS="enable_ssl=true domain=$DOMAIN"
fi

# Run the playbook
echo -e "${GREEN}Running Ansible playbook...${NC}\n"
if [ -n "$EXTRA_VARS" ]; then
    ansible-playbook -i ansible/inventory.ini ansible/playbook.yml -e "$EXTRA_VARS"
else
    ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
fi

echo -e "\n${GREEN}=========================================="
echo "Setup complete!"
echo "==========================================${NC}"

if [ "$ENABLE_SSL" = true ]; then
    echo -e "🌐 HTTPS: https://$DOMAIN"
else
    echo "🌐 HTTP: http://<your-server-ip>"
fi

echo ""
echo "To check service status: systemctl status vm-provisioner"
echo "To view logs: journalctl -u vm-provisioner -f"
echo "To restart: systemctl restart vm-provisioner"
