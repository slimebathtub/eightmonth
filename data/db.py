import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        priority INTEGER NOT NULL,
        progress_mode TEXT NOT NULL,
        progress_manual INTEGER NOT NULL,
        start_date TEXT,
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        title TEXT NOT NULL,
        done INTEGER NOT NULL,
        description TEXT,
        due_date TEXT,
        sort_order INTEGER NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS relax_item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS today_item (
        date TEXT NOT NULL,
        milestone_id INTEGER NOT NULL,
        is_done INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (date, milestone_id)
    );
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS today_relax (
        date TEXT NOT NULL,
        relax_id INTEGER NOT NULL,
        is_done INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (date, relax_id),
        FOREIGN KEY (relax_id) REFERENCES relax_item(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

    