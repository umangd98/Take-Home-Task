import os
import sqlite3

from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id TEXT,
    name          TEXT NOT NULL,
    phone         TEXT NOT NULL,
    email         TEXT NOT NULL,
    address       TEXT,
    message       TEXT NOT NULL,
    urgency       TEXT NOT NULL,
    summary       TEXT,
    after_hours   INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_events (
    event_key  TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    folder = os.path.dirname(settings.db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA)
