"""
Authentication
==============
Simple username/password auth for multi-user support. Each user gets their
own row in `users`, and every transaction/budget/memory record is scoped to
their user_id — one deployment, isolated data per person.

Passwords are hashed with bcrypt (salted, adaptive cost) — never stored or
compared in plaintext.

Note on multi-device login: session state (who's logged in) lives in each
browser's Streamlit session, not in a shared cookie/token store. That means
logging in on a laptop does not automatically log you in on your phone —
each device/browser signs in independently against the same account. This
is expected behavior, not a bug; the account and all of its data (auth,
transactions, memory) is fully shared and available from any device.
"""
import re
import sqlite3
import bcrypt

from database import db

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")
MIN_PASSWORD_LENGTH = 8


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def validate_credentials(username: str, password: str) -> str | None:
    """Returns an error message if invalid, else None."""
    if not USERNAME_RE.match((username or "").strip()):
        return "Username must be 3-32 characters: letters, numbers, '.', '_', '-' only."
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return None


def signup(username: str, password: str) -> dict:
    """Creates a new user. Returns {"success": bool, "message": str, "user": dict|None}."""
    username = (username or "").strip()
    error = validate_credentials(username, password)
    if error:
        return {"success": False, "message": error, "user": None}

    password_hash = hash_password(password)
    try:
        user_id = db.create_user(username, password_hash)
    except sqlite3.IntegrityError:
        return {"success": False, "message": "That username is already taken.", "user": None}

    return {
        "success": True,
        "message": "Account created.",
        "user": {"id": user_id, "username": username},
    }


def login(username: str, password: str) -> dict:
    """Verifies credentials. Returns {"success": bool, "message": str, "user": dict|None}."""
    username = (username or "").strip()
    user = db.get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return {"success": False, "message": "Invalid username or password.", "user": None}

    return {
        "success": True,
        "message": "Logged in.",
        "user": {"id": user["id"], "username": user["username"]},
    }
