"""
Tests for database module.
"""
import pytest
import sqlite3


class TestDatabase:
    """Test database module."""

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

    def test_init_db_creates_tables(self):
        """Test that init_db creates required tables."""
        from SQL.database import get_conn
        
        with get_conn() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            assert cursor.fetchone() is not None
            
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='vms'"
            )
            assert cursor.fetchone() is not None

    def test_users_table_schema(self):
        """Test users table has correct schema."""
        from SQL.database import get_conn
        
        with get_conn() as conn:
            cursor = conn.execute("PRAGMA table_info(users)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            assert 'id' in columns
            assert 'name' in columns
            assert 'hashed_password' in columns
            assert 'api_key_hash' in columns

    def test_vms_table_schema(self):
        """Test vms table has correct schema."""
        from SQL.database import get_conn
        
        with get_conn() as conn:
            cursor = conn.execute("PRAGMA table_info(vms)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            assert 'id' in columns
            assert 'name' in columns
            assert 'owner_id' in columns
            assert 'status' in columns
            assert 'ip' in columns
            assert 'host_port' in columns
            assert 'disk_path' in columns
            assert 'iso_path' in columns
            assert 'created_at' in columns

    def test_get_conn_context_manager(self):
        """Test get_conn works as context manager."""
        from SQL.database import get_conn
        
        with get_conn() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1

    def test_get_conn_row_factory(self):
        """Test get_conn sets row factory."""
        from SQL.database import get_conn
        
        with get_conn() as conn:
            conn.execute("INSERT INTO users (id, name, hashed_password, api_key_hash) VALUES (?, ?, ?, ?)",
                        ("test-id", "testuser", "hash", "apikeyhash"))
            conn.commit()
            
            row = conn.execute("SELECT * FROM users WHERE id = ?", ("test-id",)).fetchone()
            assert row['id'] == "test-id"
            assert row['name'] == "testuser"
