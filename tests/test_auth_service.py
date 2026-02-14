"""
Tests for auth_service module.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


class TestAuthService:
    """Test authentication service."""

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

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self):
        """Test valid API key authentication."""
        from SQL.USERS_related import add_user
        from auth_service import get_current_user
        
        add_user(
            name="testuser",
            password="password123",
            plaintext_api_key="valid-api-key"
        )
        
        user = await get_current_user(x_api_key="valid-api-key")
        
        assert user is not None
        assert user['name'] == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid(self):
        """Test invalid API key raises 401."""
        from SQL.USERS_related import add_user
        from auth_service import get_current_user
        
        add_user(
            name="testuser",
            password="password123",
            plaintext_api_key="real-key"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(x_api_key="fake-key")
        
        assert exc_info.value.status_code == 401
