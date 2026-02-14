"""
Tests for VM-related module.
"""
import pytest


class TestVMRelated:
    """Test VM management functions."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup fresh database for each test."""
        from config import DB_PATH
        from pathlib import Path
        
        db_path = Path(DB_PATH)
        if db_path.exists():
            db_path.unlink()
        
        from SQL.database import init_db
        init_db()
        
        yield

    def test_add_vm_record(self, sample_vm_record):
        """Test adding a VM record."""
        from SQL.VM_related import add_vm_record
        
        add_vm_record(sample_vm_record)

    def test_get_vm_by_id(self, sample_vm_record):
        """Test getting VM by ID."""
        from SQL.VM_related import add_vm_record, get_vm_by_id
        
        add_vm_record(sample_vm_record)
        
        vm = get_vm_by_id(sample_vm_record['id'], sample_vm_record['owner_id'])
        
        assert vm is not None
        assert vm['id'] == sample_vm_record['id']
        assert vm['name'] == sample_vm_record['name']

    def test_get_vm_by_id_not_found(self):
        """Test getting non-existent VM returns None."""
        from SQL.VM_related import get_vm_by_id
        
        vm = get_vm_by_id("nonexistent", "nonexistent-owner")
        
        assert vm is None

    def test_list_vms_by_owner(self, sample_vm_record):
        """Test listing VMs by owner."""
        from SQL.VM_related import add_vm_record, list_vms_by_owner
        
        add_vm_record(sample_vm_record)
        
        vms = list_vms_by_owner(sample_vm_record['owner_id'])
        
        assert len(vms) == 1
        assert vms[0]['id'] == sample_vm_record['id']

    def test_list_vms_by_owner_empty(self):
        """Test listing VMs for owner with no VMs."""
        from SQL.VM_related import list_vms_by_owner
        
        vms = list_vms_by_owner("nonexistent-owner")
        
        assert len(vms) == 0

    def test_update_vm_status(self, sample_vm_record):
        """Test updating VM status."""
        from SQL.VM_related import add_vm_record, update_vm_status, get_vm_by_id
        
        add_vm_record(sample_vm_record)
        
        result = update_vm_status(
            sample_vm_record['id'],
            sample_vm_record['owner_id'],
            "stopped",
            "192.168.122.200"
        )
        
        assert result is True
        
        vm = get_vm_by_id(sample_vm_record['id'], sample_vm_record['owner_id'])
        assert vm['status'] == "stopped"
        assert vm['ip'] == "192.168.122.200"

    def test_delete_vm_record(self, sample_vm_record):
        """Test deleting VM record."""
        from SQL.VM_related import add_vm_record, delete_vm_record, get_vm_by_id
        
        add_vm_record(sample_vm_record)
        
        result = delete_vm_record(
            sample_vm_record['id'],
            sample_vm_record['owner_id']
        )
        
        assert result is True
        
        vm = get_vm_by_id(sample_vm_record['id'], sample_vm_record['owner_id'])
        assert vm is None

    def test_delete_vm_record_not_owner(self, sample_vm_record):
        """Test deleting VM with wrong owner returns False."""
        from SQL.VM_related import add_vm_record, delete_vm_record
        
        add_vm_record(sample_vm_record)
        
        result = delete_vm_record(sample_vm_record['id'], "wrong-owner")
        
        assert result is False

    def test_vm_record_typeddict(self):
        """Test VMRecord TypedDict."""
        from SQL.VM_related import VMRecord
        
        vm: VMRecord = {
            "id": "test-123",
            "name": "test-vm",
            "owner_id": "owner-123",
            "status": "running",
            "host_port": 2222,
            "disk_path": "/path/to/disk.qcow2",
            "iso_path": "/path/to/iso.iso",
            "created_at": "2024-01-01T00:00:00"
        }
        
        assert vm['id'] == "test-123"
        assert vm['status'] == "running"
