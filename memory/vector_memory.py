"""
Persistent Conversation Memory
===============================
Gives the agent semantic recall across sessions, per user, backed by a
Chroma vector store persisted to disk (survives app restarts — unlike a
prototype that only kept memory in Streamlit's session_state for the
lifetime of one browser tab).

Two kinds of records are stored per user, in the same collection but tagged
by `kind` in metadata:
  - "chat"       — every user/assistant turn, so the agent can recall things
                    like "I told you I'm saving for a laptop" weeks later.
  - "preference" — things worth remembering longer-term and surfacing more
                    proactively (e.g. "I want to cut down on food delivery").

Chroma's default embedding function (a small local ONNX MiniLM model) is
used, so no external embedding API key is required — this keeps the whole
memory feature runnable offline.

Cross-platform note: chromadb requires SQLite >= 3.35, but several common
environments (older macOS system Python, some Linux distros, Streamlit
Community Cloud) ship an older bundled `sqlite3`. That mismatch is one of
the most common reasons this kind of app runs fine on one machine and
crashes with `RuntimeError: Your system has an unsupported version of
sqlite3` on another. The shim below transparently swaps in the
`pysqlite3-binary` wheel (modern SQLite, statically linked, no system
dependency) when it's available and needed, before chromadb is imported
anywhere in the process.
"""
import os
import sys
import time
import uuid

# --- sqlite3 compatibility shim (must run before `import chromadb`) -------
try:
    import sqlite3 as _system_sqlite3
    _needs_shim = tuple(int(p) for p in _system_sqlite3.sqlite_version.split(".")[:3]) < (3, 35, 0)
except Exception:
    _needs_shim = True

if _needs_shim:
    try:
        __import__("pysqlite3")
        sys.modules["sqlite3"] = sys.modules["pysqlite3"]
    except ImportError:
        # pysqlite3-binary isn't installed (e.g. unsupported platform/arch).
        # Leave the system sqlite3 in place; chromadb will raise a clear
        # error if it truly can't run, rather than failing silently here.
        pass

import chromadb  # noqa: E402  (import order is intentional, see shim above)

PERSIST_DIR = os.environ.get(
    "CHROMA_PERSIST_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma_db"),
)

_client = None
_client_lock_dir = None


def _get_client():
    global _client
    if _client is None:
        os.makedirs(PERSIST_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=PERSIST_DIR)
    return _client


class ConversationMemory:
    """One instance per user_id. Cheap to construct — call it per request."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        client = _get_client()
        self.collection = client.get_or_create_collection(
            name=f"user_{user_id}_memory",
            metadata={"hnsw:space": "cosine"},
        )

    def add_chat_turn(self, role: str, content: str):
        """role: 'user' or 'assistant'"""
        if not content or not content.strip():
            return
        self._add(content, kind="chat", extra={"role": role})

    def add_preference(self, text: str):
        """Store a longer-term fact/preference about the user."""
        if not text or not text.strip():
            return
        self._add(text, kind="preference", extra={"role": "user"})

    def _add(self, text: str, kind: str, extra: dict):
        doc_id = f"{kind}-{uuid.uuid4().hex}"
        metadata = {"kind": kind, "timestamp": time.time(), **extra}
        self.collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])

    def retrieve_relevant(self, query: str, k: int = 5, kinds=("chat", "preference")) -> list[dict]:
        """Semantic search over this user's memory. Returns list of
        {"text": str, "kind": str, "role": str, "timestamp": float}."""
        count = self.collection.count()
        if count == 0 or not query or not query.strip():
            return []

        where = {"kind": {"$in": list(kinds)}} if kinds else None
        results = self.collection.query(
            query_texts=[query],
            n_results=min(k, count),
            where=where,
        )

        out = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        for doc, meta in zip(docs, metas):
            out.append({
                "text": doc,
                "kind": meta.get("kind"),
                "role": meta.get("role"),
                "timestamp": meta.get("timestamp"),
            })
        return out

    def get_context_string(self, query: str, k: int = 5) -> str:
        """Formats relevant memories as a block to inject into the agent's
        system prompt. Returns "" if nothing relevant / no history yet."""
        memories = self.retrieve_relevant(query, k=k)
        if not memories:
            return ""

        lines = []
        for m in memories:
            tag = "preference" if m["kind"] == "preference" else m.get("role", "note")
            lines.append(f"- ({tag}) {m['text']}")
        return "Relevant memory from past conversations with this user:\n" + "\n".join(lines)

    def clear(self):
        """Wipes this user's memory (e.g. for a 'forget everything' action)."""
        client = _get_client()
        try:
            client.delete_collection(name=f"user_{self.user_id}_memory")
        except Exception:
            pass  # collection may already be empty/missing — fine
        self.collection = client.get_or_create_collection(
            name=f"user_{self.user_id}_memory",
            metadata={"hnsw:space": "cosine"},
        )
