"""
Tests for cloudinit module.
"""
import pytest
from pathlib import Path


class TestCloudInit:
    """Test cloud-init ISO generation."""

    def test_render_template(self):
        """Test template rendering."""
        from cloudinit import render_template
        
        result = render_template("user-data.yaml.j2", {
            "name": "test-vm",
            "username": "debian",
            "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB test@example.com"
        })
        
        assert "test-vm" in result
        assert "debian" in result
        assert "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB" in result

    def test_render_user_data_template(self):
        """Test user-data.yaml.j2 rendering."""
        from cloudinit import render_template
        
        result = render_template("user-data.yaml.j2", {
            "name": "my-vm",
            "username": "ubuntu",
            "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB test"
        })
        
        assert "#cloud-config" in result
        assert "hostname: my-vm" in result
        assert "name: ubuntu" in result
        assert "sudo: ALL=(ALL) NOPASSWD:ALL" in result
        assert "ssh_authorized_keys:" in result

    def test_render_meta_data_template(self):
        """Test meta-data.yaml.j2 rendering."""
        from cloudinit import render_template
        
        result = render_template("meta-data.yaml.j2", {
            "vm_id": "test-uuid-123",
            "name": "my-vm"
        })
        
        assert "instance-id: test-uuid-123" in result
        assert "hostname: my-vm" in result

    def test_create_config_iso_debian(self):
        """Test creating cloud-init ISO for Debian."""
        from cloudinit import create_config_iso
        from config import CLOUD_INIT_DIR
        
        vm_id = "test-vm-123"
        ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB test"
        
        iso_path = create_config_iso(
            vm_id=vm_id,
            name="test-vm",
            image_type="debian-12",
            ssh_key=ssh_key
        )
        
        assert iso_path.exists()
        assert str(iso_path).endswith(".iso")
        assert vm_id in str(iso_path)

    def test_create_config_iso_rocky(self):
        """Test creating cloud-init ISO for Rocky Linux."""
        from cloudinit import create_config_iso
        
        iso_path = create_config_iso(
            vm_id="test-vm-456",
            name="rocky-vm",
            image_type="rocky-9",
            ssh_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB test"
        )
        
        assert iso_path.exists()

    def test_create_config_iso_alpine(self):
        """Test creating cloud-init ISO for Alpine."""
        from cloudinit import create_config_iso
        
        iso_path = create_config_iso(
            vm_id="test-vm-789",
            name="alpine-vm",
            image_type="alpine",
            ssh_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB test"
        )
        
        assert iso_path.exists()

    def test_delete_config_iso(self):
        """Test deleting cloud-init ISO."""
        from cloudinit import create_config_iso, delete_config_iso
        
        vm_id = "test-vm-delete"
        
        iso_path = create_config_iso(
            vm_id=vm_id,
            name="test-vm",
            image_type="debian-12",
            ssh_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB test"
        )
        
        assert iso_path.exists()
        
        delete_config_iso(vm_id)
        
        assert not iso_path.exists()

    def test_delete_nonexistent_iso(self):
        """Test deleting non-existent ISO doesn't raise error."""
        from cloudinit import delete_config_iso
        
        delete_config_iso("nonexistent-vm")
