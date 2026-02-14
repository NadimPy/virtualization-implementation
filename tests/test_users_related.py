"""
Tests for users-related module.
"""
import pytest
import hashlib


class TestUsersRelated:
    """Test user management functions."""

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

    def test_hash_api_key(self):
        """Test API key hashing."""
        from SQL.USERS_related import hash_api_key
        
        api_key = "test-api-key-123"
        expected_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        result = hash_api_key(api_key)
        
        assert result == expected_hash

    def test_hash_api_key_different_keys(self):
        """Test different API keys produce different hashes."""
        from SQL.USERS_related import hash_api_key
        
        hash1 = hash_api_key("key1")
        hash2 = hash_api_key("key2")
        
        assert hash1 != hash2

    def test_hash_password_function(self):
        """Test password hashing function exists."""
        from SQL.USERS_related import hash_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password

    def test_verify_password_function(self):
        """Test password verification function using SHA256 fallback."""
        from SQL.USERS_related import hash_password, verify_password
        
        password = "mysecretpassword"
        
        # Use SHA256 fallback for testing
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_add_user(self):
        """Test adding a user."""
        from SQL.USERS_related import add_user
        
        result = add_user(
            name="testuser",
            password="password123",
            plaintext_api_key="test-api-key"
        )
        
        assert result is not None
        assert result['name'] == "testuser"
        assert 'id' in result
        assert 'api_key_hash' in result

    def test_add_duplicate_api_key(self):
        """Test adding user with duplicate API key returns None."""
        from SQL.USERS_related import add_user
        
        result1 = add_user(
            name="user1",
            password="password1",
            plaintext_api_key="same-key"
        )
        assert result1 is not None
        
        result2 = add_user(
            name="user2",
            password="password2",
            plaintext_api_key="same-key"
        )
        assert result2 is None

    def test_get_user_by_api_key(self):
        """Test getting user by API key."""
        from SQL.USERS_related import add_user, get_user_by_api_key
        
        add_user(
            name="testuser",
            password="password123",
            plaintext_api_key="my-api-key"
        )
        
        user = get_user_by_api_key("my-api-key")
        
        assert user is not None
        assert user['name'] == "testuser"

    def test_get_user_by_invalid_api_key(self):
        """Test getting user with invalid API key returns None."""
        from SQL.USERS_related import add_user, get_user_by_api_key
        
        add_user(
            name="testuser",
            password="password123",
            plaintext_api_key="real-key"
        )
        
        user = get_user_by_api_key("fake-key")
        
        assert user is None
