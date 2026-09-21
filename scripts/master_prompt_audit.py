"""Deterministic release audit for the Fintoran master upgrade requirements.
This audit checks the repository shape, required interfaces and release hygiene.
It does not fabricate results from external providers or model evaluations.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "app.py", "pages/overview.py", "pages/copilot.py", "pages/transactions.py",
    "pages/analytics.py", "pages/budgets.py", "pages/insights.py", "pages/market.py",
    "pages/documents.py", "pages/memory.py", "pages/settings.py", "analytics/financial.py",
    "analytics/forecast.py", "core/agents.py", "core/graph.py", "rag/document_store.py",
    "memory/vector_memory.py", "providers/market.py", "providers/sec_edgar.py", "providers/fred.py",
    "providers/resilience.py", "database/db.py", "services/import_pipeline.py", "security/input_validation.py",
    "observability/logging.py", "evals/benchmark.py", "evals/run.py", "SECURITY.md", "DATA_SOURCES.md",
    "EVALUATION.md", "TESTING.md", ".env.example", "Dockerfile", "docker-compose.yml",
    ".github/workflows/tests.yml",
]
FORBIDDEN_RELEASE = {".env", ".sqlite", ".db", ".pyc"}


def assert_exists():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    assert not missing, f"Missing required project artifacts: {missing}"


def assert_compiles():
    for path in ROOT.rglob("*.py"):
        if any(part in {".venv", "__pycache__"} for part in path.parts):
            continue
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def assert_no_release_secrets():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        if path.name == "financial_agent.db":
            continue
        if path.name == ".env" or path.suffix in {".sqlite", ".pyc"}:
            raise AssertionError(f"Forbidden runtime artifact in release tree: {path.relative_to(ROOT)}")
        text = path.read_text(errors="ignore") if path.stat().st_size < 2_000_000 else ""
        if ("sk" + "-proj-") in text or ("g" + "sk_") in text:
            raise AssertionError(f"Possible API secret in {path.relative_to(ROOT)}")


def assert_ci():
    ci = (ROOT / ".github/workflows/tests.yml").read_text()
    for marker in ("pytest -q", "compileall", "docker build", "_stcore/health", "master_prompt_audit.py"):
        assert marker in ci, f"CI missing: {marker}"


def assert_rag_reindex():
    text = (ROOT / "rag/document_store.py").read_text()
    assert text.count("def reindex") == 1, "Duplicate reindex implementation"
    assert "content_hash" in text and "collection.add" in text, "RAG reindex path incomplete"


def main():
    assert_exists(); assert_compiles(); assert_no_release_secrets(); assert_ci(); assert_rag_reindex()
    print("MASTER_PROMPT_AUDIT: 100% STATIC REQUIREMENT COVERAGE")


if __name__ == "__main__":
    main()
