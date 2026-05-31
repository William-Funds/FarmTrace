"""
FarmTrace — SQLite database layer
All tables created on first run. Thread-safe via check_same_thread=False + WAL mode.
"""
import sqlite3, os, logging
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'farmtrace.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ts          TEXT    NOT NULL,
        temp_c      REAL,
        humidity    REAL,
        soil_pct    REAL,
        lat         REAL,
        lon         REAL,
        synced      INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS batches (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id        TEXT UNIQUE NOT NULL,
        crop_type       TEXT NOT NULL,
        buyer_name      TEXT,
        buyer_email     TEXT,
        target_kg       REAL,
        current_kg      REAL DEFAULT 0,
        status          TEXT DEFAULT 'open',
        created_at      TEXT NOT NULL,
        locked_at       TEXT,
        passport_path   TEXT,
        passport_hash   TEXT,
        synced          INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS parcels (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id     TEXT NOT NULL,
        farmer_name  TEXT NOT NULL,
        farmer_id    TEXT,
        weight_kg    REAL NOT NULL,
        lat          REAL,
        lon          REAL,
        location_name TEXT,
        harvest_date TEXT,
        photo_path   TEXT,
        added_at     TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sync_queue (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        record_type TEXT NOT NULL,
        record_id   INTEGER,
        payload     TEXT,
        attempts    INTEGER DEFAULT 0,
        last_error  TEXT,
        created_at  TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()
    logging.info("Database initialised at %s", DB_PATH)
