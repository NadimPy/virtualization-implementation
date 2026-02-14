import sqlite3

create_table_query = """
CREATE TABLE IF NOT EXISTS VMs (
    id TEXT,
    name TEXT,
    status TEXT,
    created_at TEXT,
    disk_path TEXT
);
"""
with sqlite3.connect('example.db') as connection:
    cursor = connection.cursor()
    cursor.execute(create_table_query)


