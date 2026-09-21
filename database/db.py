"""SQLite repository layer with user-scoped financial and document metadata."""
from __future__ import annotations

import hashlib
import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterable

_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financial_agent.db")
DB_PATH = os.environ.get("DB_PATH", _DEFAULT_DB_PATH)
_lock = threading.RLock()

_SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        category TEXT,
        is_recurring INTEGER DEFAULT 0,
        is_anomaly INTEGER DEFAULT 0,
        merchant TEXT,
        currency TEXT DEFAULT 'INR',
        source TEXT,
        source_hash TEXT,
        imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS budgets (
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        monthly_limit REAL NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, category),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS import_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT,
        source TEXT,
        source_hash TEXT,
        row_count INTEGER NOT NULL DEFAULT 0,
        accepted_count INTEGER NOT NULL DEFAULT 0,
        rejected_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        document_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        mime_type TEXT,
        source TEXT DEFAULT 'user_upload',
        page_count INTEGER DEFAULT 0,
        chunk_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, content_hash),
        UNIQUE(user_id, document_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS user_profiles (
        user_id INTEGER PRIMARY KEY,
        base_currency TEXT NOT NULL DEFAULT 'INR',
        monthly_income REAL,
        financial_goals TEXT,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""",
]

_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_txn_user_date ON transactions(user_id, date)",
    "CREATE INDEX IF NOT EXISTS idx_txn_user_category ON transactions(user_id, category)",
    "CREATE INDEX IF NOT EXISTS idx_txn_user_merchant ON transactions(user_id, merchant)",
    "CREATE INDEX IF NOT EXISTS idx_txn_user_source_hash ON transactions(user_id, source_hash)",
    "CREATE INDEX IF NOT EXISTS idx_import_user_created ON import_batches(user_id, created_at)",
    "CREATE INDEX IF NOT EXISTS idx_docs_user_created ON documents(user_id, created_at)",
]


def _migrate_columns(conn: sqlite3.Connection) -> None:
    migrations = {
        "transactions": {
            "merchant": "TEXT",
            "currency": "TEXT DEFAULT 'INR'",
            "source": "TEXT",
            "source_hash": "TEXT",
            "imported_at": "TEXT",
        },
        "budgets": {"updated_at": "TEXT"},
    }
    for table, columns in migrations.items():
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, spec in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {spec}")
    conn.execute("UPDATE transactions SET imported_at = COALESCE(imported_at, CURRENT_TIMESTAMP)")
    conn.execute("UPDATE budgets SET updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)")
    conn.execute("INSERT OR IGNORE INTO user_profiles(user_id) SELECT id FROM users")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    with _lock:
        for statement in _SCHEMA:
            conn.execute(statement)
        _migrate_columns(conn)
        for statement in _INDEXES:
            conn.execute(statement)
        conn.commit()
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.close()


@contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Users

def create_user(username: str, password_hash: str) -> int:
    with transaction() as conn:
        cur = conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        return int(cur.lastrowid)


def get_user_by_username(username: str):
    with transaction() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int):
    with transaction() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


# Transactions

def clear_transactions(user_id: int):
    with transaction() as conn:
        conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))


def insert_transactions(user_id: int, rows: Iterable[dict]):
    rows = list(rows)
    if not rows:
        return
    prepared = []
    for raw in rows:
        row = dict(raw)
        row["user_id"] = user_id
        row.setdefault("merchant", row.get("description", ""))
        row.setdefault("currency", "INR")
        row.setdefault("source", "unknown")
        row.setdefault("source_hash", None)
        prepared.append(row)
    with transaction() as conn:
        conn.executemany(
            """INSERT INTO transactions
            (user_id,date,description,amount,type,category,is_recurring,is_anomaly,merchant,currency,source,source_hash)
            VALUES (:user_id,:date,:description,:amount,:type,:category,:is_recurring,:is_anomaly,:merchant,:currency,:source,:source_hash)""",
            prepared,
        )


def get_all_transactions(user_id: int):
    with transaction() as conn:
        rows = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date, id", (user_id,)).fetchall()
        return [dict(r) for r in rows]


def get_transactions(user_id: int, *, limit: int | None = None, category: str | None = None):
    sql = "SELECT * FROM transactions WHERE user_id = ?"
    args: list = [user_id]
    if category:
        sql += " AND category = ?"
        args.append(category)
    sql += " ORDER BY date DESC, id DESC"
    if limit:
        sql += " LIMIT ?"
        args.append(limit)
    with transaction() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def update_transaction_category(user_id: int, transaction_id: int, category: str) -> bool:
    with transaction() as conn:
        cur = conn.execute("UPDATE transactions SET category = ? WHERE id = ? AND user_id = ?", (category, transaction_id, user_id))
        return cur.rowcount == 1


# Budgets

def set_budget(user_id: int, category: str, limit: float):
    with transaction() as conn:
        conn.execute(
            """INSERT INTO budgets(user_id,category,monthly_limit) VALUES(?,?,?)
            ON CONFLICT(user_id,category) DO UPDATE SET monthly_limit=excluded.monthly_limit, updated_at=CURRENT_TIMESTAMP""",
            (user_id, category, limit),
        )


def get_budgets(user_id: int):
    with transaction() as conn:
        rows = conn.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,)).fetchall()
        return {r["category"]: r["monthly_limit"] for r in rows}


def create_import_batch(user_id: int, filename: str, source: str, source_hash: str, row_count: int, accepted_count: int, rejected_count: int) -> int:
    with transaction() as conn:
        cur = conn.execute(
            "INSERT INTO import_batches(user_id,filename,source,source_hash,row_count,accepted_count,rejected_count) VALUES(?,?,?,?,?,?,?)",
            (user_id, filename, source, source_hash, row_count, accepted_count, rejected_count),
        )
        return int(cur.lastrowid)


def has_import_hash(user_id: int, source_hash: str) -> bool:
    with transaction() as conn:
        return bool(conn.execute("SELECT 1 FROM import_batches WHERE user_id=? AND source_hash=? LIMIT 1", (user_id, source_hash)).fetchone())


def list_import_batches(user_id: int):
    with transaction() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM import_batches WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()]


def upsert_document(user_id: int, document_id: str, filename: str, content_hash: str, mime_type: str, page_count: int, chunk_count: int):
    with transaction() as conn:
        conn.execute(
            """INSERT INTO documents(user_id,document_id,filename,content_hash,mime_type,page_count,chunk_count)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(user_id,content_hash) DO UPDATE SET filename=excluded.filename,mime_type=excluded.mime_type,page_count=excluded.page_count,chunk_count=excluded.chunk_count,updated_at=CURRENT_TIMESTAMP""",
            (user_id, document_id, filename, content_hash, mime_type, page_count, chunk_count),
        )


def get_documents(user_id: int):
    with transaction() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM documents WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()]


def delete_document_record(user_id: int, document_id: str) -> bool:
    with transaction() as conn:
        cur = conn.execute("DELETE FROM documents WHERE user_id=? AND document_id=?", (user_id, document_id))
        return cur.rowcount == 1


def reset_user_data(user_id: int) -> None:
    with transaction() as conn:
        conn.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM budgets WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM import_batches WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM documents WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM user_profiles WHERE user_id=?", (user_id,))


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_user_profile(user_id: int):
    with transaction() as conn:
        row=conn.execute('SELECT * FROM user_profiles WHERE user_id=?',(user_id,)).fetchone()
        return dict(row) if row else {'user_id':user_id,'base_currency':'INR','monthly_income':None,'financial_goals':None}

def update_user_profile(user_id: int, base_currency='INR', monthly_income=None, financial_goals=None):
    with transaction() as conn:
        conn.execute('INSERT INTO user_profiles(user_id,base_currency,monthly_income,financial_goals) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET base_currency=excluded.base_currency,monthly_income=excluded.monthly_income,financial_goals=excluded.financial_goals,updated_at=CURRENT_TIMESTAMP',(user_id,base_currency,monthly_income,financial_goals))
