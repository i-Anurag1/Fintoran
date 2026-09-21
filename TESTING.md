# Testing

## Local validation

1. Install dependencies.
2. Run `pytest -q`.
3. Run `python -m compileall -q .`.
4. Run `python scripts/smoke_test.py`.
5. Run `python evals/run.py`.
6. Run `python scripts/master_prompt_audit.py`.
7. Start Streamlit with `streamlit run app.py`.
8. Test signup, login, CSV import preview, replacement confirmation, dashboard, chat, budgets, analytics, market provider failure, document ingestion, RAG citations, document re-indexing, memory reset, and logout.

## CI

GitHub Actions installs the dependency set on Python 3.11 and 3.12, runs compile checks, pytest, smoke tests, the master prompt audit, the evaluation manifest, then builds and health-checks the Docker image.

## External services

Unit tests should mock yfinance, news search, SEC, FRED, and model calls. The application is designed to run without external market/news providers and without FRED. Groq is required only for live AI Copilot model execution.

## Docker

```bash
docker build -t fintoran .
docker run --rm -p 8501:8501 --env-file .env fintoran
```

Healthcheck endpoint:

```text
/_stcore/health
```
