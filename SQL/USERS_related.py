import sqlite3
import uuid
import logging
import hashlib
from .database import get_conn

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash - always uses SHA256 for simplicity."""
    # Always use SHA256 for verification (simpler and consistent)
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def hash_api_key(plaintext_key: str) -> str:
    """Hash API key for DB storage and lookup."""
    return hashlib.sha256(plaintext_key.encode()).hexdigest()

def add_user(name: str, password: str, plaintext_api_key: str) -> dict | None:
    user_id = str(uuid.uuid4())
    api_key_hash = hash_api_key(plaintext_api_key)
    hashed_password = hash_password(password)
    
    try:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO users (id, name, hashed_password, api_key_hash)
                   VALUES (?, ?, ?, ?)""",
                (user_id, name, hashed_password, api_key_hash)
            )
            conn.commit()
        logger.info(f"User {name} added")
        return {"id": user_id, "name": name, "api_key_hash": api_key_hash}
    except sqlite3.IntegrityError:
        logger.warning(f"Duplicate API key for user {name}")
        return None
    except Exception as err:
        logger.error(f"Database error: {err}")
        raise

def get_user_by_api_key(plaintext_api_key: str) -> dict | None:
    """Lookup user by plaintext API key (hashed for comparison)."""
    api_key_hash = hash_api_key(plaintext_api_key)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, api_key_hash FROM users WHERE api_key_hash = ?",
            (api_key_hash,)
        ).fetchone()
        return dict(row) if row else None

def get_user_by_api_key_hash(plaintext_api_key: str) -> dict | None:
    """Lookup user by plaintext API key (hashed for comparison)."""
    api_key_hash = hash_api_key(plaintext_api_key)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, api_key_hash FROM users WHERE api_key_hash = ?",
            (api_key_hash,)
        ).fetchone()
        return dict(row) if row else None