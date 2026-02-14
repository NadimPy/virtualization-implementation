import sqlite3
from contextlib import contextmanager
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH") or str(Path("/var/lib/vm-provisioner/vms.db"))

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                api_key_hash TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS vms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                status TEXT NOT NULL,
                ip TEXT,
                host_port INTEGER UNIQUE NOT NULL,
                disk_path TEXT NOT NULL,
                iso_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()