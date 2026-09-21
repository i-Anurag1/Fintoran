import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def temp_db(monkeypatch, tmp_path):
    """Points the db module at a fresh SQLite file for this test only."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    from database import db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", str(db_path))
    db_module.init_db()
    return db_module


@pytest.fixture()
def temp_chroma_dir(monkeypatch, tmp_path):
    """Points vector_memory at a fresh Chroma persist dir for this test only."""
    chroma_dir = tmp_path / "chroma_db"
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(chroma_dir))

    import memory.vector_memory as vm
    monkeypatch.setattr(vm, "PERSIST_DIR", str(chroma_dir))
    monkeypatch.setattr(vm, "_client", None)
    return vm


@pytest.fixture()
def sample_user(temp_db):
    from auth import auth
    result = auth.signup("alice", "correcthorsebattery")
    assert result["success"]
    return result["user"]
