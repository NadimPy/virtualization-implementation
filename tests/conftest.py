"""
Pytest configuration and shared fixtures for VM Provisioner tests.
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path

# Set test environment variables BEFORE importing anything else
os.environ['DATA_DIR'] = '/tmp/vm-provisioner-test'
os.environ['DB_PATH'] = '/tmp/vm-provisioner-test/vms.db'
os.environ['LIBVIRT_URI'] = 'test:///default'
os.environ['START_PORT'] = '2222'
os.environ['END_PORT'] = '2322'

# Ensure test data directory exists
TEST_DATA_DIR = '/tmp/vm-provisioner-test'
os.makedirs(TEST_DATA_DIR, exist_ok=True)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def test_data_dir(temp_dir):
    """Create test data directories."""
    data_dir = temp_dir / "data"
    data_dir.mkdir()
    (data_dir / "images").mkdir()
    (data_dir / "instances").mkdir()
    (data_dir / "cloud-init").mkdir()
    return data_dir


@pytest.fixture
def sample_vm_record():
    """Sample VM record for testing."""
    return {
        "id": "test-vm-123",
        "name": "test-vm",
        "owner_id": "test-user-123",
        "status": "running",
        "ip": "192.168.122.100",
        "host_port": 2222,
        "disk_path": "/tmp/vm-provisioner-test/instances/test-vm-123.qcow2",
        "iso_path": "/tmp/vm-provisioner-test/cloud-init/test-vm-123.iso",
        "created_at": "2024-01-01T00:00:00",
        "image_type": "debian-12"
    }


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return {
        "id": "test-user-123",
        "name": "testuser",
        "api_key_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    }
