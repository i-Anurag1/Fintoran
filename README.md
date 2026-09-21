# Fintoran

Fintoran is an agentic personal-finance workspace built around deterministic financial tooling, LangGraph orchestration, private semantic memory, document RAG, market research, and user-scoped data.

## Product scope

Fintoran combines five layers:

1. Deterministic finance services for balances, spending, budgets, forecasts, anomalies, recurring payments, trends, and scenarios.
2. A LangGraph supervisor that routes work to personal-finance, market, analytics, and document/RAG specialists.
3. Per-user Chroma memory for conversation context and a separate per-user document knowledge store.
4. Provider adapters for market data, SEC EDGAR public filing data, and optional FRED macro data.
5. A Streamlit application with authenticated navigation, import review, provenance, diagnostics, and safe fallbacks.

Fintoran is informational software. It is not a licensed financial adviser.

## Architecture

```text
                         Streamlit application
                                  |
                    +-------------+-------------+
                    |                           |
                 User auth                 Navigation
                    |                           |
                    +-------------+-------------+
                                  |
                         AI Copilot / pages
                                  |
                         LangGraph Supervisor
             +------------+-------+--------+------------+
             |            |                |            |
       Personal Finance  Market        Analytics    Document/RAG
             |            |                |            |
          SQLite      Provider APIs   deterministic   Chroma
             |                           Python         |
             +-----------------------------+------------+
                                  |
                       User-scoped persistence
```

The LLM interprets results. It is never the source of truth for arithmetic, balances, transaction counts, dates, budget calculations, or forecast calculations.

## Features

### Existing functionality preserved

- Streamlit application and light theme
- bcrypt authentication
- user-scoped transactions and budgets
- SQLite local persistence
- Chroma conversation memory
- LangGraph Supervisor -> Budget Agent / Market Agent workflow
- LangChain tool calling
- Groq model fallback chain
- finance tools for summaries, budgets, affordability, forecasts, anomalies, and recurring payments
- yfinance market data
- financial news search through `ddgs`
- CSV dataset loading
- sample and historical dataset files
- Docker and docker-compose
- GitHub Actions
- pytest suite

### Upgrade functionality

- Multipage application using `st.Page` and `st.navigation`
- Overview dashboard with deterministic metrics
- CSV import pipeline: raw -> validated -> normalized -> enriched -> stored
- column detection, validation, duplicate import detection, preview, rejection report, provenance, and explicit replacement
- category and merchant normalization
- transaction export
- daily/monthly spending trends
- category trends and merchant concentration
- percentile outliers and explainable anomaly signals
- naive, moving-average, and weighted-moving-average forecast comparison
- deterministic scenario analysis
- analytics specialist agent
- document/RAG specialist agent
- PDF, TXT, Markdown, and CSV document ingestion
- Chroma document retrieval with per-user filters, document/page metadata, citations, deletion, duplicate detection, private-source integrity checks, and re-indexing
- SEC EDGAR adapter for public submissions and XBRL company facts
- optional FRED adapter when `FRED_API_KEY` is supplied
- market-data provenance and freshness metadata, historical risk metrics, moving averages, volume, and fundamentals
- structured route metadata with confidence, evidence, and tool-plan fields plus final-answer metadata
- provider-safe error handling and graceful degradation
- structured application logging with correlation IDs and secret redaction
- upload size and path validation
- private-data isolation checks at the database and vector-store layer
- evaluation fixtures and deterministic benchmark definitions
- security, testing, data-source, and evaluation documentation

## Data policy

Fintoran labels data by source and freshness. A public dataset is not treated as live data.

Supported labels include:

- demo/synthetic
- historical public dataset
- live/delayed market data
- SEC filing data
- FRED macro data
- user-uploaded private data

External data responses include provider and retrieval timestamps where the provider supports it.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Open the displayed local Streamlit URL, create an account, and load a dataset or import a CSV.

## Environment variables

Required for AI Copilot:

- `GROQ_API_KEY`

Optional:

- `GROQ_MODEL`
- `GROQ_FALLBACK_MODELS`
- `DB_PATH`
- `CHROMA_PERSIST_DIR`
- `CHROMA_DOCUMENTS_DIR`
- `PRIVATE_DOCUMENT_DIR`
- `FRED_API_KEY`
- `SEC_USER_AGENT`
- `MAX_SUPERVISOR_STEPS`
- `MAX_UPLOAD_BYTES`
- `MAX_DOCUMENT_BYTES`

## Docker

```bash
cp .env.example .env
# add GROQ_API_KEY

docker compose up --build
```

The image uses a non-root runtime user, a healthcheck, and named persistent volumes. Secrets are passed through the environment and are not baked into the image.

## Testing

Dependency installation and full tests:

```bash
pip install -r requirements.txt
pytest -q
```

Dependency-light smoke test:

```bash
python scripts/smoke_test.py
```

Compile/import syntax check:

```bash
python -m compileall -q .
```

Evaluation fixture inspection:

```bash
python evals/run.py
python scripts/master_prompt_audit.py
```

See `TESTING.md` for the full validation matrix and known external-service limitations.

## Project structure

```text
app.py
pages/
ui/
core/
tools/
analytics/
services/
providers/
rag/
memory/
database/
auth/
security/
observability/
evals/
scripts/
tests/
data/
```

## Security and privacy

See `SECURITY.md` for authentication, user isolation, upload controls, prompt-injection handling, logs, and export safety.

Uploaded private documents are processed through the RAG service and are not stored under Streamlit's static/public directory.

## Limitations

- Market data freshness depends on the upstream provider.
- FRED requires an API key.
- SEC access requires a meaningful `User-Agent` and adherence to SEC access guidance.
- Indian market data licensing is provider-dependent. Fintoran does not bypass exchange restrictions.
- Forecast uncertainty intervals are not fabricated. The current forecast layer reports model choice and historical holdout error where enough history exists.
- Browser-level end-to-end automation is not included in the repository because the development environment does not guarantee a browser runner.
- Full pytest and Docker verification require dependency installation and container tooling. The repository includes CI for those checks.

## Resume-ready description

- Built a multi-agent personal finance platform with LangGraph Supervisor routing across finance, market, analytics, and document-RAG specialists, with typed route metadata and bounded execution.
- Implemented deterministic financial analytics and modular forecast evaluation, separating Python calculations from LLM reasoning for balances, budgets, anomalies, trends, and month-end scenarios.
- Built per-user document RAG with Chroma, metadata filters, source/page citations, duplicate detection, deletion, and prompt-injection-resistant retrieval context.
- Hardened the application with bcrypt auth, user-scoped SQLite repositories, upload validation, provenance tracking, structured logs, provider fallbacks, Docker, CI, and evaluation fixtures.
