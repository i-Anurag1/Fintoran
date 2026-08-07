"""
Database layer — SQLite, multi-user.

Every transaction and budget row is scoped to a user_id (FK -> users.id).
The default DB path is resolved relative to this file (not the process's
current working directory), so the app behaves the same whether it's
launched with `streamlit run app.py` from the project root, from a
different directory, or inside Docker — this is what previously caused
"works on my laptop, not on others" style failures when the app was
launched from a different working directory.

TODO (future iteration): swap for PostgreSQL for real concurrent
multi-user deployments; the query shapes here map over directly.
"""
import os
import sqlite3
import threading

_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "financial_agent.db")
DB_PATH = os.environ.get("DB_PATH", _DEFAULT_DB_PATH)

_lock = threading.Lock()

_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        category TEXT,
        is_recurring INTEGER DEFAULT 0,
        is_anomaly INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS budgets (
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        monthly_limit REAL NOT NULL,
        PRIMARY KEY (user_id, category),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_txn_user ON transactions(user_id)",
]


def get_connection():
    """Every connection self-heals the schema (CREATE TABLE IF NOT EXISTS is
    cheap) before returning, so any function in this module works correctly
    even if init_db() was never explicitly called first — e.g. a script or
    test that only touches one function directly, on a brand-new DB file.
    This is what `check_budget_status(some_user_with_no_data, ...)` relies
    on: it should gracefully report "no data" rather than crash with
    'no such table'."""
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # WAL mode gives much better behavior under concurrent Streamlit
    # sessions (multiple browser tabs / users hitting the same file).
    conn.execute("PRAGMA journal_mode = WAL")
    with _lock:
        for statement in _SCHEMA_STATEMENTS:
            conn.execute(statement)
        conn.commit()
    return conn


def init_db():
    """Kept as an explicit, named setup step for callers (e.g. app.py) that
    want to initialize up front — but get_connection() now does this too,
    so calling init_db() is a convenience, not a requirement."""
    conn = get_connection()
    conn.close()


# ---------------- Users ----------------

def create_user(username: str, password_hash: str) -> int:
    """Inserts a new user. Raises sqlite3.IntegrityError if username taken."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------- Transactions (user-scoped) ----------------

def clear_transactions(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def insert_transactions(user_id: int, rows):
    """rows: list of dicts with date, description, amount, type, category,
    is_recurring, is_anomaly. user_id here is always the source of truth —
    any 'user_id' key already present in a row dict is overwritten, and the
    caller's dicts are never mutated (each row is copied first). This
    matters if the same row dict/template is reused across multiple calls
    for different users, which previously caused one user's data to
    silently end up attributed to another."""
    if not rows:
        return
    conn = get_connection()
    cur = conn.cursor()
    prepared = []
    for r in rows:
        row = dict(r)
        row["user_id"] = user_id
        prepared.append(row)
    cur.executemany("""
        INSERT INTO transactions (user_id, date, description, amount, type, category, is_recurring, is_anomaly)
        VALUES (:user_id, :date, :description, :amount, :type, :category, :is_recurring, :is_anomaly)
    """, prepared)
    conn.commit()
    conn.close()


def get_all_transactions(user_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Budgets (user-scoped) ----------------

def set_budget(user_id: int, category: str, limit: float):
    conn = get_connection()
    conn.execute("""
        INSERT INTO budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)
        ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = excluded.monthly_limit
    """, (user_id, category, limit))
    conn.commit()
    conn.close()


def get_budgets(user_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM budgets WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["category"]: r["monthly_limit"] for r in rows}
