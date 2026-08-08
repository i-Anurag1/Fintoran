  # Financial Agent — Agentic AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" />
  <img src="https://img.shields.io/badge/LangGraph-Agent%20Orchestration-purple" />
  <img src="https://img.shields.io/badge/LangChain-1.0-green" />
  <img src="https://img.shields.io/badge/Docker-Ready-blue" />
  <img src="https://img.shields.io/badge/CI-GitHub%20Actions-black" />
</p>

<p align="center">
  An intelligent personal finance platform powered by multi-agent AI,
  semantic memory, financial analytics, and real-time market intelligence.
</p>

<p align="center">
  🚀 Live Demo: https://fintoran.streamlit.app/
</p>


**Status:** Multi-agent prototype with auth, persistent memory, Docker deployment, and CI.
A personal finance system where a Supervisor LLM routes each question to
specialist sub-agents, which autonomously decide which tools to call — not
a fixed pipeline, this revision hardens it into five production-shaped pieces: multi-agent orchestration
(LangGraph), persistent semantic memory, multi-user authentication, Docker
deployment, and an automated test suite.

## What changed in this revision

| Area | Before | Now |
|---|---|---|
| **Orchestration** | Older `langgraph.prebuilt.create_react_agent` API, deprecated `set_entry_point` | Migrated to the stable **LangChain 1.0 `create_agent`** API (with automatic fallback for older installs) and modern `START`/`END` graph edges |
| **Model reliability** | Hardcoded `llama-3.3-70b-versatile`, which Groq has deprecated (shutdown Aug 16, 2026) — the likely cause of intermittent agent errors | Default switched to Groq's current `openai/gpt-oss-120b`; if a model call fails for any reason (deprecated, renamed, rate-limited), the orchestrator automatically retries with the next model in a fallback chain instead of crashing the turn; individual specialist-agent failures are caught and reported instead of taking down the whole response |
| **Cross-device reliability** | Crashed on machines with an older system `sqlite3` (a common cause of "works on my laptop, not others/phone") | Transparent `pysqlite3-binary` shim so Chroma always gets a modern SQLite, regardless of the OS's bundled version |
| **News search** | `duckduckgo-search`, which its maintainer **froze and renamed to `ddgs`** | Migrated to the maintained **`ddgs`** package, with a legacy fallback |
| **File paths** | Dataset/upload paths were relative to the process's working directory, breaking if launched from anywhere but the project root | All paths resolved relative to the source file, not the current working directory |
| **Memory** | Chat history lived only in Streamlit `session_state` (gone on refresh) | Every chat turn + preference is embedded and stored in a per-user **Chroma vector store on disk**, retrieved by semantic similarity and injected into the Supervisor's context on every turn |
| **Users** | — | **bcrypt-hashed accounts**; every transaction, budget, and memory record is scoped to `user_id`. (Login is per-browser/device by design — see note below.) |
| **Deployment** | — | `Dockerfile` (non-root user, healthcheck) + `docker-compose.yml` with persisted named volumes for the DB and vector store — works identically on Linux, macOS, and Windows |
| **Testing** | — | `pytest` suite covering DB scoping, auth, finance tool logic, mocked market tools, memory isolation, and the supervisor's routing/handoff logic, wired into **GitHub Actions CI** on every push |
| **UI** | Emoji-heavy, fixed two-column layout | Light, low-emoji, professional theme (`.streamlit/config.toml`); reasoning trace moved into an expander so it reads cleanly on both desktop and mobile |


Two real, common causes were fixed here:

1. **SQLite version mismatch.** Chroma (the vector memory store) requires
   SQLite ≥ 3.35. Some machines — especially older macOS system Python
   installs, some Linux distros, and some cloud runtimes — ship an older
   bundled SQLite and crash with `RuntimeError: Your system has an
   unsupported version of sqlite3` the moment memory is used. `pysqlite3-binary`
   is now installed and swapped in automatically when needed
   (`memory/vector_memory.py`), so this no longer depends on the host OS.
2. **Working-directory-relative paths.** Loading a bundled dataset or an
   uploaded CSV used paths like `"data/kaggle_transactions.csv"`, which
   only resolve correctly if the app happens to be launched from the
   project root. All paths are now anchored to the app's own file
   location instead.

One thing that is **not** a bug and can't be "fixed" away: **logging in
is per-browser/device**, because Streamlit's session state isn't a shared
cookie store. Signing in on your phone after signing in on your laptop is
expected — it's the same account either way, with the same data.

## Architecture

```
                         User question (chat, per logged-in user)
                                       │
                                       ▼
                     Vector memory retrieves relevant past
                     context for this user (memory/vector_memory.py)
                                       │
                                       ▼
                    Supervisor (core/graph.py, LangGraph)
              — reads question + memory context —
              — decides: budget_agent, market_agent, or FINISH —
                        ┌──────────────┴──────────────┐
                        ▼                              ▼
                 Budget Agent                    Market Agent
            (core/agents.py + tools/          (core/agents.py + tools/
             finance_tools.py)                 market_tools.py)
             • transaction summary             • live stock price (yfinance)
             • budget vs. actual                • analyst recommendations
             • month-end forecast               • financial news (ddgs)
             • afford-check reasoning
             • anomaly detection
             • recurring payment detection
                        │                              │
                        ▼                              ▼
              SQLite, scoped to user_id          External APIs (live internet)
              (database/db.py)
                        │
                        └──────────────┬───────────────┘
                                       ▼
                     Supervisor loops (cap: 6 steps) until FINISH
                                       ▼
                        Synthesize node produces final answer
                                       │
                                       ▼
                    New turn embedded + stored in vector memory
```

The Supervisor can call either specialist multiple times in any order —
e.g. for "should I buy AAPL or pay off my card?" it might route to the
Market Agent for the price, then the Budget Agent for affordability, then
synthesize one answer across both. Nobody hardcodes that sequence; the
Supervisor LLM decides it per-question via structured-output tool routing.

# 🛠️ Tech Stack


| Category | Technology |
|---|---|
| Language | Python |
| AI Framework | LangChain |
| Agent Workflow | LangGraph |
| LLM Provider | Groq |
| Default Model | openai/gpt-oss-120b |
| Memory Database | ChromaDB |
| Database | SQLite |
| Authentication | bcrypt |
| Finance Data | yfinance |
| News Search | ddgs |
| Frontend | Streamlit |
| Containerization | Docker |
| Testing | Pytest |
| CI/CD | GitHub Actions |



## Quick Start (local, no Docker)

Requires Python 3.10+.

```bash
git clone <your-repo-url>
cd financial-agent
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then add your free Groq API key
streamlit run app.py
```

Get a free API key at [console.groq.com/keys](https://console.groq.com/keys).

On first load you'll see a **sign-up / log-in** screen. Create an account
(username 3-32 chars, password 8+ chars) — everything after that (data,
chat history, memory) is scoped to that account and available from any
device you log into it from. Then, in the sidebar, click **"Load Kaggle
Dataset"** or **"Load Synthetic Test Data"**, go to the **Chat** tab, and
ask something like:
- *"Can I afford a ₹15,000 phone this month?"*
- *"What's TCS.NS trading at right now?"*
- *"Am I overspending on food and dining?"*
- *"Should I buy AAPL stock or pay off my credit card bill first?"*

## Quick Start (Docker)

```bash
cp .env.example .env              # add your GROQ_API_KEY
docker compose up --build
```

Visit `http://localhost:8501`. The SQLite database and Chroma vector store
are persisted in named Docker volumes (`db_data`, `chroma_data`), so
accounts, transactions, and memory survive container restarts — and this
works the same on Linux, macOS, and Windows hosts since named volumes
avoid the path/permission quirks of bind mounts.

## Running the tests

```bash
pip install -r requirements.txt   # includes pytest
pytest
```

Tests use isolated temp SQLite DBs and temp Chroma dirs per test (see
`tests/conftest.py`), and mock the LLM, sub-agents, `yfinance`, and
`ddgs` — no API key or network access needed to run the suite. They also
run automatically on every push/PR via `.github/workflows/tests.yml`.

Coverage:
- `test_db.py` — user creation, per-user transaction/budget isolation
- `test_auth.py` — password hashing, signup validation, login success/failure
- `test_finance_tools.py` — categorization, summaries, budgets, forecasting, affordability, anomaly detection, recurring payments
- `test_market_tools.py` — stock price / recommendations / news, with mocked external APIs (including error handling and the `ddgs`/legacy-package fallback)
- `test_memory.py` — semantic add/retrieve, per-user isolation, context formatting, clearing
- `test_graph.py` — Supervisor routing, multi-agent chaining/ordering, max-step capping, end-to-end orchestrator run — all with a mocked LLM and mocked sub-agents

## Datasets

Two datasets ship with the project, each proving a different thing on purpose:

| Dataset | File | Rows | Use it to demo |
|---|---|---|---|
| **Kaggle (real)** | `data/kaggle_transactions.csv` | 1,500, spanning 2020–2024 | Scale, categorization, budget tracking, forecasting, multi-tool reasoning |
| **Synthetic (built for testing)** | `data/sample_transactions.csv` | 358, spanning 6 months | Recurring-payment detection and anomaly detection specifically |

**Data quality note:** the Kaggle file has all 146 "Salary" transactions
typed as `Expense` rather than `Income`. `convert_dataset.py` detects and
flags this automatically rather than silently correcting it.

To convert any other dataset you download later:
```bash
python convert_dataset.py path/to/downloaded_file.csv data/your_output_name.csv
```

## Tech Stack

| Component | Choice | Why |
|---|---|---|
| LLM | Groq (`openai/gpt-oss-120b`, with automatic fallback to `gpt-oss-20b` / `llama-3.3-70b-versatile` if a model is unavailable) | Free tier, fast inference, native tool calling; not tied to a single model that Groq could deprecate |
| Orchestration | LangChain 1.0 `create_agent` + LangGraph `StateGraph` (Supervisor + 2 specialist agents) | Real multi-agent handoff, transparent state graph, current stable API |
| Persistent memory | Chroma (local, on-disk, per-user collections) | Semantic recall across sessions, no external API key needed (local embedding model) |
| Auth | bcrypt + SQLite `users` table | Simple, no external dependency, salted adaptive hashing |
| Market data | yfinance | Free, no key needed, real live prices |
| News search | `ddgs` (maintained successor to `duckduckgo-search`) | Free, no key needed |
| Storage | SQLite (WAL mode), user-scoped | Zero-setup, swappable for Postgres later |
| UI | Streamlit, light theme | Fast to build, works on desktop and mobile browsers |
| Deployment | Docker (non-root) + docker-compose | Reproducible, persisted named volumes |
| Testing | pytest + pytest-mock + GitHub Actions | Fast, no network/API key required, runs on every push |

## Project Structure

```
financial-agent/
├── core/
│   ├── graph.py             # Supervisor StateGraph — routing, handoffs, synthesis
│   └── agents.py            # Budget Agent + Market Agent (LangChain create_agent)
├── auth/
│   └── auth.py              # signup/login, bcrypt hashing
├── memory/
│   └── vector_memory.py     # per-user Chroma-backed semantic memory
├── tools/
│   ├── finance_tools.py     # user-scoped personal finance logic
│   └── market_tools.py      # live stock price, analyst data, news search
├── database/
│   └── db.py                # SQLite layer — users, transactions, budgets (all user-scoped)
├── tests/                   # pytest suite (see above)
├── data/
│   ├── kaggle_transactions.csv
│   └── sample_transactions.csv
├── .streamlit/
│   └── config.toml          # light theme
├── .github/workflows/
│   └── tests.yml            # CI — runs pytest on push/PR
├── app.py                   # Streamlit UI — login, chat, reasoning trace, data view
├── convert_dataset.py       # CSV normalizer for new datasets
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── pytest.ini
```

## Deploying

- **Streamlit Community Cloud:** point it at this repo, set `GROQ_API_KEY`
  in the app's Secrets, and deploy — no code changes needed. The
  `pysqlite3-binary` shim specifically targets this kind of managed
  environment, where you don't control the host's system SQLite.
- **Docker / any VPS:** `docker compose up --build -d` and put a reverse
  proxy (Caddy/Nginx) with TLS in front of port 8501 if exposing it
  publicly.

  ---

## Troubleshooting

### SQLite Version Error

If you see:

```bash
RuntimeError: Your system has an unsupported version of sqlite3
```

The project automatically handles this using `pysqlite3-binary`.

Make sure dependencies are installed correctly:

```bash
pip install -r requirements.txt
```

---

### API Key Error

If the application shows LLM connection errors:

Check your `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Restart the application after updating environment variables.

---

### Docker Issues

Rebuild containers after dependency changes:

```bash
docker compose down

docker compose up --build
```

---

## Dataset Support

The project includes sample transaction datasets for testing and demonstration.

Available datasets:

| Dataset | File | Purpose |
|---|---|---|
| Kaggle Transactions | `data/kaggle_transactions.csv` | Real transaction analysis |
| Synthetic Transactions | `data/sample_transactions.csv` | Testing anomaly and recurring payment detection |

To convert a custom CSV dataset:

```bash
python convert_dataset.py input.csv output.csv
```

---

## Example Queries

Try asking Fintoran:

```text
Can I afford a ₹15000 phone this month?

Analyze my spending habits.

Where am I spending the most money?

Show my monthly budget status.

What is the current price of AAPL?

Should I invest or save money?
```

---

## Testing

Run the complete test suite:

```bash
pytest
```

Tests cover:

- Authentication flow
- Database isolation
- Finance calculations
- Market data tools
- Vector memory
- Agent routing
- Multi-agent workflow

GitHub Actions runs tests automatically on every push and pull request.

---

## Project Structure

```text
financial-agent/

├── core/
│   ├── graph.py
│   └── agents.py
│
├── auth/
│   └── auth.py
│
├── memory/
│   └── vector_memory.py
│
├── tools/
│   ├── finance_tools.py
│   └── market_tools.py
│
├── database/
│   └── db.py
│
├── tests/
│
├── data/
│   ├── kaggle_transactions.csv
│   └── sample_transactions.csv
│
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Future Improvements

- Voice based financial assistant
- Mobile application
- Banking API integration
- Advanced investment analysis
- Portfolio management
- More specialized AI agents
- Cloud database migration

---

## Developer

Built by Anurag Thakur

B.Tech Computer Science Engineering

Focus Areas:

- Agentic AI
- Backend Engineering
- Distributed Systems
- Financial Technology

---

## License

This project is developed for educational and research purposes.

### SQLite Version Error

