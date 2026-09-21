from __future__ import annotations

import hashlib
import io
import os
import re
import uuid
from datetime import datetime, timezone

from database import db
from security.input_validation import validate_filename, validate_upload_size

MAX_CHUNK = 1000
OVERLAP = 150
PRIVATE_DOC_DIR = os.getenv(
    "PRIVATE_DOCUMENT_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "private_documents"),
)


def _client():
    import chromadb
    path = os.getenv(
        "CHROMA_DOCUMENTS_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "document_chroma"),
    )
    os.makedirs(path, exist_ok=True)
    return chromadb.PersistentClient(path=path)


def _extract(filename, data):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
        except ImportError as exc:
            raise ValueError("PDF support requires pypdf") from exc
    return [(1, data.decode("utf-8-sig", errors="replace"))]


def _chunks(text):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    step = max(1, MAX_CHUNK - OVERLAP)
    return [text[i : i + MAX_CHUNK] for i in range(0, len(text), step)]


def _private_path(document_id: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return os.path.join(PRIVATE_DOC_DIR, str(document_id) + ext)


def ingest(user_id, filename, data, mime_type="text/plain"):
    filename = validate_filename(filename)
    validate_upload_size(data)
    digest = hashlib.sha256(data).hexdigest()
    existing = [d for d in db.get_documents(user_id) if d["content_hash"] == digest]
    if existing:
        return {"status": "duplicate", "document": existing[0]}

    document_id = uuid.uuid4().hex
    collection = _client().get_or_create_collection(
        name=f"user_{user_id}_documents", metadata={"hnsw:space": "cosine"}
    )
    ids, chunks, metadatas = [], [], []
    pages = _extract(filename, data)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    for page, text in pages:
        for idx, chunk in enumerate(_chunks(text)):
            ids.append(f"{document_id}:{page}:{idx}")
            chunks.append(chunk)
            metadatas.append(
                {
                    "user_id": str(user_id),
                    "document_id": document_id,
                    "filename": filename,
                    "page": page,
                    "chunk": idx,
                    "source": "user_upload",
                    "content_hash": digest,
                    "retrieved_at": retrieved_at,
                }
            )
    if chunks:
        collection.add(ids=ids, documents=chunks, metadatas=metadatas)

    user_dir = os.path.join(PRIVATE_DOC_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    private_path = _private_path(document_id, filename)
    with open(private_path, "wb") as fh:
        fh.write(data)
    try:
        os.chmod(private_path, 0o600)
    except OSError:
        pass

    db.upsert_document(user_id, document_id, filename, digest, mime_type, len(pages), len(chunks))
    return {
        "status": "success",
        "document": {
            "document_id": document_id,
            "filename": filename,
            "chunks": len(chunks),
            "retrieved_at": retrieved_at,
        },
    }


def search(user_id, query, k=5, document_id=None):
    collection = _client().get_or_create_collection(
        name=f"user_{user_id}_documents", metadata={"hnsw:space": "cosine"}
    )
    if collection.count() == 0:
        return []
    where = {"user_id": str(user_id)}
    if document_id:
        where = {"$and": [where, {"document_id": document_id}]}
    result = collection.query(
        query_texts=[query],
        n_results=min(max(1, k), collection.count()),
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text": text,
            "metadata": metadata,
            "distance": distance,
            "citation": f"{metadata.get('filename')} p.{metadata.get('page')}",
        }
        for text, metadata, distance in zip(
            result.get("documents", [[]])[0],
            result.get("metadatas", [[]])[0],
            result.get("distances", [[]])[0],
        )
    ]


def delete(user_id, document_id):
    collection = _client().get_or_create_collection(
        name=f"user_{user_id}_documents", metadata={"hnsw:space": "cosine"}
    )
    collection.delete(where={"$and": [{"user_id": str(user_id)}, {"document_id": document_id}]})
    docs = db.get_documents(user_id)
    target = next((d for d in docs if d["document_id"] == document_id), None)
    if target:
        path = _private_path(document_id, target["filename"])
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
    return db.delete_document_record(user_id, document_id)


def reindex(user_id, document_id):
    """Rebuild one user's document vectors from its private source bytes."""
    docs = db.get_documents(user_id)
    target = next((d for d in docs if d["document_id"] == document_id), None)
    if not target:
        return {"status": "error", "message": "Document not found."}

    path = _private_path(document_id, target["filename"])
    if not os.path.isfile(path):
        return {
            "status": "error",
            "message": "Original private document bytes are unavailable. Upload the document again to re-index it.",
        }

    try:
        with open(path, "rb") as fh:
            data = fh.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != target["content_hash"]:
            return {"status": "error", "message": "Private source integrity check failed. Re-upload the document."}

        collection = _client().get_or_create_collection(
            name=f"user_{user_id}_documents", metadata={"hnsw:space": "cosine"}
        )
        collection.delete(where={"$and": [{"user_id": str(user_id)}, {"document_id": document_id}]})

        pages = _extract(target["filename"], data)
        ids, chunks, metadatas = [], [], []
        retrieved_at = datetime.now(timezone.utc).isoformat()
        for page, text in pages:
            for idx, chunk in enumerate(_chunks(text)):
                ids.append(f"{document_id}:{page}:{idx}")
                chunks.append(chunk)
                metadatas.append(
                    {
                        "user_id": str(user_id),
                        "document_id": document_id,
                        "filename": target["filename"],
                        "page": page,
                        "chunk": idx,
                        "source": "user_upload",
                        "content_hash": digest,
                        "retrieved_at": retrieved_at,
                    }
                )
        if chunks:
            collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        db.upsert_document(
            user_id,
            document_id,
            target["filename"],
            digest,
            target.get("mime_type") or "application/octet-stream",
            len(pages),
            len(chunks),
        )
        return {"status": "success", "document_id": document_id, "chunks": len(chunks), "retrieved_at": retrieved_at}
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception:
        return {"status": "error", "message": "Document re-indexing is unavailable right now."}


def reset_user_documents(user_id):
    docs = db.get_documents(user_id)
    for document in docs:
        delete(user_id, document["document_id"])
    user_dir = os.path.join(PRIVATE_DOC_DIR, str(user_id))
    if os.path.isdir(user_dir):
        for name in os.listdir(user_dir):
            path = os.path.join(user_dir, name)
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except OSError:
                pass
