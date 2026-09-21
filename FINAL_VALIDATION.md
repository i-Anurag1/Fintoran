# Final validation record

This release was built from the supplied Fintoran archive in a separate working copy. The supplied source archive was not modified.

## Validation completed in this build environment

- Python compile check: passed
- Dependency-light smoke test: passed
- Offline evaluation manifest: passed
- Core SQLite/auth/finance/import/analytics/security/market tests: 37 passed
- Graph and Chroma tests: skipped only because `langchain_core` and `chromadb` are not installed in this offline build environment
- Secret scan: passed after excluding placeholder environment variable names and documentation examples
- Release tree cleanup: passed
- Runtime database/private document data/cache/log cleanup before packaging: passed
- Dockerfile and GitHub Actions configuration included

## Environment limitation

The build environment has no outbound package-index/network access and does not have the full application dependency set installed. Therefore live Streamlit startup, LangGraph execution with a real LangChain installation, Chroma retrieval, external provider calls, and Docker build/start were not executable here.

The repository keeps the full dependency declarations in `requirements.txt`, and CI installs those dependencies before running the complete suite.

## Exact offline commands run

```bash
python -m compileall -q .
python scripts/smoke_test.py
python evals/run.py
PYTHONPATH=/usr/lib/python3/dist-packages pytest -q
```

Observed test result in this environment:

```text
37 passed, 2 skipped
```

The two skipped tests are dependency-gated Graph and Chroma tests. No test failures remain among the tests executable in this environment.

## Required networked validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m compileall -q .
python scripts/smoke_test.py
python evals/run.py
streamlit run app.py
```

For Docker:

```bash
docker build -t fintoran:latest .
docker compose up --build -d
curl -f http://localhost:8501/_stcore/health
```

For external services, configure `GROQ_API_KEY`, and configure `SEC_USER_AGENT` and `FRED_API_KEY` only when those providers are used.

No benchmark quality scores are claimed without executing the model evaluation against the configured model and fixtures.
