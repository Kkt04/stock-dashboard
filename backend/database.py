"""
Database initialization and connection management using SQLite.
"""

import sqlite3
import os

# Use /tmp for Vercel serverless, local data folder otherwise
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/stocks.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stocks.db")


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed with mock data if empty."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            symbol      TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            sector      TEXT,
            exchange    TEXT DEFAULT 'NSE'
        );

        CREATE TABLE IF NOT EXISTS stock_prices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT NOT NULL,
            date        TEXT NOT NULL,
            open        REAL,
            high        REAL,
            low         REAL,
            close       REAL,
            volume      INTEGER,
            UNIQUE(symbol, date)
        );

        CREATE INDEX IF NOT EXISTS idx_symbol_date
            ON stock_prices(symbol, date);
    """)
    conn.commit()

    # Seed only if empty
    count = cur.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    if count == 0:
        print("Seeding database with mock data...")
        from scripts.seed_data import seed

        seed(conn)
        print("Database seeded.")

    conn.close()
