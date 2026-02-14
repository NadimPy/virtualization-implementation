"""
Tests for storage module.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import importlib


class TestStorage:
    """Test storage functions."""

    def test_clone_base_image_template_not_found(self):
        """Test error when template not found."""
        # Remove template if exists from previous test
        template_path = Path('/tmp/vm-provisioner-test/images/debian-12-template.qcow2')
        if template_path.exists():
            template_path.unlink()
        
        # Need fresh import to use test config
        import storage
        importlib.reload(storage)
        
        with pytest.raises(FileNotFoundError, match="Template not found"):
            storage.clone_base_image("test-vm-id", "debian-12")

    def test_clone_base_image_with_mock(self):
        """Test cloning base image with mocked qemu-img."""
        # Create template in test dir
        template_path = Path('/tmp/vm-provisioner-test/images/debian-12-template.qcow2')
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.touch()
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        import storage
        original_run = storage.subprocess.run
        storage.subprocess.run = mock_result
        
        try:
            result = storage.clone_base_image("test-vm-id", "debian-12")
            assert result.name == "test-vm-id.qcow2"
            mock_result.assert_called_once()
        finally:
            storage.subprocess.run = original_run

    def test_delete_disk_image(self):
        """Test deleting disk image."""
        disk_path = Path('/tmp/vm-provisioner-test/instances/test-vm.qcow2')
        disk_path.parent.mkdir(parents=True, exist_ok=True)
        disk_path.touch()
        
        assert disk_path.exists()
        
        import storage
        importlib.reload(storage)
        storage.delete_disk_image("test-vm")
        
        assert not disk_path.exists()

    def test_delete_disk_image_nonexistent(self):
        """Test deleting non-existent disk doesn't raise."""
        import storage
        importlib.reload(storage)
        
        # Should not raise
        storage.delete_disk_image("nonexistent-vm")

    def test_get_disk_info_file_not_found(self):
        """Test error when disk not found."""
        import storage
        importlib.reload(storage)
        
        with pytest.raises(FileNotFoundError, match="Disk not found"):
            storage.get_disk_info("nonexistent-vm")

    def test_resize_disk(self):
        """Test resizing disk."""
        disk_path = Path('/tmp/vm-provisioner-test/instances/test-vm.qcow2')
        disk_path.parent.mkdir(parents=True, exist_ok=True)
        disk_path.touch()
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        import storage
        original_run = storage.subprocess.run
        storage.subprocess.run = mock_result
        
        try:
            storage.resize_disk("test-vm", 20)
            mock_result.assert_called_once()
            call_args = mock_result.call_args[0][0]
            assert 'qemu-img' in call_args
            assert 'resize' in call_args
            assert '20G' in call_args
        finally:
            storage.subprocess.run = original_run
