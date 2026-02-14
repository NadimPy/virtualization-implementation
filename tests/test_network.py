"""
Tests for network module.
"""
import pytest


class TestNetwork:
    """Test network functions."""

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

    def test_generate_mac_address(self):
        """Test MAC address generation."""
        from network import generate_mac_address
        
        vm_id = "test-vm-uuid-123"
        mac = generate_mac_address(vm_id)
        
        assert mac.startswith("52:54:00:")
        
        parts = mac.split(":")
        assert len(parts) == 6
        
        for part in parts:
            assert len(part) == 2
            assert all(c in "0123456789abcdef" for c in part)

    def test_generate_mac_address_deterministic(self):
        """Test MAC address generation is deterministic."""
        from network import generate_mac_address
        
        vm_id = "test-uuid"
        
        mac1 = generate_mac_address(vm_id)
        mac2 = generate_mac_address(vm_id)
        
        assert mac1 == mac2

    def test_generate_mac_address_unique(self):
        """Test different VM IDs produce different MACs."""
        from network import generate_mac_address
        
        mac1 = generate_mac_address("vm-1")
        mac2 = generate_mac_address("vm-2")
        
        assert mac1 != mac2

    def test_allocate_port_first(self):
        """Test allocating first port."""
        from network import allocate_port
        
        port = allocate_port()
        
        assert port == 2222

    def test_allocate_port_increment(self, sample_vm_record):
        """Test port allocation increments."""
        from network import allocate_port
        from SQL.VM_related import add_vm_record
        
        add_vm_record(sample_vm_record)
        
        port = allocate_port()
        
        assert port == 2223

    def test_allocate_port_no_available(self):
        """Test error when no ports available."""
        from network import allocate_port
        from SQL.VM_related import add_vm_record
        
        for i in range(101):
            vm = {
                "id": f"vm-{i}",
                "name": f"vm-{i}",
                "owner_id": "test-owner",
                "status": "running",
                "host_port": 2222 + i,
                "disk_path": f"/path/{i}.qcow2",
                "iso_path": f"/path/{i}.iso",
                "created_at": "2024-01-01T00:00:00",
                "ip": f"192.168.122.{i+1}"
            }
            add_vm_record(vm)
        
        with pytest.raises(RuntimeError, match="No available ports"):
            allocate_port()

    def test_port_range(self):
        """Test port range configuration."""
        from config import START_PORT, END_PORT
        
        assert START_PORT == 2222
        assert END_PORT == 2322
        assert END_PORT > START_PORT
