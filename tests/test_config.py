"""
Tests for config module.
"""
import pytest
from pathlib import Path


class TestConfig:
    """Test configuration module."""

    def test_images_config(self):
        """Test VM images configuration."""
        from config import IMAGES
        
        assert 'debian-12' in IMAGES
        assert 'rocky-9' in IMAGES
        assert 'alpine' in IMAGES
        
        for image_type, image_config in IMAGES.items():
            assert 'name' in image_config
            assert 'template_path' in image_config
            assert 'username' in image_config

    def test_image_debian(self):
        """Test Debian image configuration."""
        from config import IMAGES
        
        debian = IMAGES['debian-12']
        assert debian['name'] == 'Debian 12 (Bookworm)'
        assert debian['username'] == 'debian'

    def test_image_rocky(self):
        """Test Rocky Linux image configuration."""
        from config import IMAGES
        
        rocky = IMAGES['rocky-9']
        assert rocky['name'] == 'Rocky Linux 9'
        assert rocky['username'] == 'rocky'

    def test_image_alpine(self):
        """Test Alpine image configuration."""
        from config import IMAGES
        
        alpine = IMAGES['alpine']
        assert alpine['name'] == 'Alpine Linux'
        assert alpine['username'] == 'alpine'

    def test_base_directories(self):
        """Test base directory paths are Path objects."""
        from config import DATA_DIR, IMAGE_DIR, INSTANCE_DIR, CLOUD_INIT_DIR, TEMPLATE_DIR
        
        assert isinstance(DATA_DIR, Path)
        assert isinstance(IMAGE_DIR, Path)
        assert isinstance(INSTANCE_DIR, Path)
        assert isinstance(CLOUD_INIT_DIR, Path)
        assert isinstance(TEMPLATE_DIR, Path)

    def test_libvirt_uri_default(self):
        """Test Libvirt URI from environment."""
        from config import LIBVIRT_URI
        
        # Should be the value from .env or default
        assert LIBVIRT_URI is not None

    def test_cloud_init_label(self):
        """Test cloud-init ISO label."""
        from config import CLOUD_INIT_ISO_LABEL
        
        assert CLOUD_INIT_ISO_LABEL == 'cidata'
