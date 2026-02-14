import sqlite3
import logging
from database import get_conn

logger = logging.getLogger(__name__)

from typing import TypedDict, NotRequired

class VMRecord(TypedDict):
    id: str
    name: str
    owner_id: str
    status: str
    ip: NotRequired[str]
    host_port: int
    disk_path: str
    iso_path: str
    created_at: str

def add_vm_record(vm: VMRecord) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO vms (id, name, owner_id, status, host_port, 
                              disk_path, iso_path, created_at, ip)
               VALUES (:id, :name, :owner_id, :status, :host_port,
                       :disk_path, :iso_path, :created_at, :ip)""",
            vm
        )
        conn.commit()
        logger.info(f"VM {vm['name']} added for owner {vm['owner_id']}")

def get_vm_by_id(vm_id: str, owner_id: str) -> VMRecord | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM vms WHERE id = ? AND owner_id = ?",
            (vm_id, owner_id)
        ).fetchone()
        return dict(row) if row else None

def list_vms_by_owner(owner_id: str) -> list[VMRecord]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM vms WHERE owner_id = ? ORDER BY created_at DESC",
            (owner_id,)
        ).fetchall()
        return [dict(row) for row in rows]

def update_vm_status(vm_id: str, owner_id: str, status: str, ip: str | None = None) -> bool:
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE vms SET status = ?, ip = ? 
               WHERE id = ? AND owner_id = ?""",
            (status, ip, vm_id, owner_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_vm_record(vm_id: str, owner_id: str) -> bool:
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM vms WHERE id = ? AND owner_id = ?",
            (vm_id, owner_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def list_vms_by_owner(owner_id: str) -> list[VMRecord]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM vms WHERE owner_id = ? ORDER BY created_at DESC",
            (owner_id,)
        ).fetchall()
        return [dict(row) for row in rows]

def update_vm_status(vm_id: str, owner_id: str, status: str, ip: str | None = None) -> bool:
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE vms SET status = ?, ip = ? 
               WHERE id = ? AND owner_id = ?""",
            (status, ip, vm_id, owner_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_vm_record(vm_id: str, owner_id: str) -> bool:
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM vms WHERE id = ? AND owner_id = ?",
            (vm_id, owner_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def get_vm_by_id_for_update(vm_id: str, owner_id: str) -> VMRecord | None:
    """Get VM with row locking for status updates."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM vms WHERE id = ? AND owner_id = ?",
            (vm_id, owner_id)
        ).fetchone()
        return dict(row) if row else None

