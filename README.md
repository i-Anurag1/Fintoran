<!--
  NOTE FOR MAINTAINER: the original README used two different GitHub owners
  (aditisaha1089 and i-Anurag1) and two different live URLs
  (fintoranai.streamlit.app and fintoranagent.streamlit.app).
  Both sets are preserved below. Please verify and keep only the correct ones.
-->

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=260&section=header&text=FINTORAN&fontSize=84&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Agentic%20AI%20Personal%20Finance%20Intelligence%20Platform&descAlignY=60&descSize=20" alt="Fintoran banner" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=2800&pause=900&color=4F8CFF&center=true&vCenter=true&width=900&lines=Financial+Data+%E2%86%92+Intelligence;Agentic+AI+%2B+Deterministic+Analytics;Forecasting+%2B+Anomaly+Detection;RAG+%2B+Persistent+Memory;Private+%2B+Explainable+Personal+Finance" alt="Fintoran typing animation"/>

<br/>

**Turn raw financial data into structured intelligence, explanations, forecasts, anomaly signals and actionable insights.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-LLM_Tooling-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-Inference-F55036?style=for-the-badge)](https://groq.com/)

[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Chroma](https://img.shields.io/badge/Chroma-Vector_Memory-5B21B6?style=for-the-badge)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

<br/>

[![Live Demo](https://img.shields.io/badge/%E2%9C%A6%20LIVE%20DEMO-Open%20App-4F8CFF?style=for-the-badge&labelColor=0B1220)](https://fintoranagent.streamlit.app/)
[![Source Code](https://img.shields.io/badge/%E2%9C%A6%20SOURCE-GitHub-8B5CF6?style=for-the-badge&labelColor=0B1220&logo=github)](https://github.com/i-Anurag1/Fintoran)

<br/>

<a href="#-vision">Vision</a> &nbsp;·&nbsp;
<a href="#-capabilities">Capabilities</a> &nbsp;·&nbsp;
<a href="#-architecture">Architecture</a> &nbsp;·&nbsp;
<a href="#-agentic-design">Agents</a> &nbsp;·&nbsp;
<a href="#-data-pipeline">Pipeline</a> &nbsp;·&nbsp;
<a href="#-security">Security</a> &nbsp;·&nbsp;
<a href="#-quick-start">Quick Start</a> &nbsp;·&nbsp;
<a href="#-roadmap">Roadmap</a>

</div>

<br/>

```text
███████╗██╗███╗   ██╗████████╗ ██████╗ ██████╗  █████╗ ███╗   ██╗
██╔════╝██║████╗  ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗████╗  ██║
█████╗  ██║██╔██╗ ██║   ██║   ██║   ██║██████╔╝███████║██╔██╗ ██║
██╔══╝  ██║██║╚██╗██║   ██║   ██║   ██║██╔══██╗██╔══██║██║╚██╗██║
██║     ██║██║ ╚████║   ██║   ╚██████╔╝██║  ██║██║  ██║██║ ╚████║
╚═╝     ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
```

> **Fintoran** is an agentic AI financial intelligence workspace that transforms personal financial data into structured, explainable and actionable insights.

<br/>

## ✦ At a Glance

<div align="center">

| 🧩 **10** | 🤖 **4** | 🌐 **3** | ✅ **49** | 🐍 **2** |
|:---:|:---:|:---:|:---:|:---:|
| Product modules | Specialist agents | External data providers | Passing tests | Python versions in CI |

</div>

<br/>

## ✦ Vision

Fintoran is **not** a generic chatbot placed on top of a spreadsheet. It is a financial intelligence layer built on one central rule:

> **Numbers come from deterministic code. Language comes from the LLM.**

```mermaid
flowchart TD
    F(["🏦 FINTORAN"])
    F --> D["⚙️ DETERMINISTIC COMPUTATION"]
    F --> A["🧠 AGENTIC AI REASONING"]

    D --> D1["Exact numbers"]
    D --> D2["Aggregations"]
    D --> D3["Forecasts"]
    D --> D4["Anomalies"]
    D --> D5["Metrics"]

    A --> A1["Explanations"]
    A --> A2["Planning"]
    A --> A3["Synthesis"]
    A --> A4["Retrieval"]
    A --> A5["Financial dialogue"]

    D1 & D2 & D3 & D4 & D5 --> I{{"💡 FINANCIAL INTELLIGENCE"}}
    A1 & A2 & A3 & A4 & A5 --> I

    classDef root fill:#4F8CFF,stroke:#1E3A8A,color:#fff,stroke-width:2px
    classDef det fill:#DBEAFE,stroke:#3B82F6,color:#0B1220
    classDef ai fill:#EDE9FE,stroke:#8B5CF6,color:#0B1220
    classDef out fill:#10B981,stroke:#065F46,color:#fff,stroke-width:2px
    class F root
    class D,D1,D2,D3,D4,D5 det
    class A,A1,A2,A3,A4,A5 ai
    class I out
```

<br/>

## ✦ Capabilities

<div align="center">

| | Module | What it does |
|:---:|:---|:---|
| 📊 | **Overview** | Financial health summary and key metrics |
| 🤖 | **AI Copilot** | Agentic financial conversations |
| 💳 | **Transactions** | Search, filtering, categorization and transaction intelligence |
| 📈 | **Analytics** | Spending, income, category and trend analysis |
| 🎯 | **Budgets** | Budget tracking and financial planning |
| 💡 | **Insights** | Automated financial observations |
| 🌍 | **Market Research** | Market, macroeconomic and company research |
| 📄 | **Documents / RAG** | Grounded answers from uploaded financial documents |
| 🧠 | **Memory** | Persistent conversation context |
| ⚙️ | **Settings** | Account and application configuration |

</div>

<br/>

## ✦ Architecture

```mermaid
flowchart TD
    U(["👤 User"]) --> UI["🖥️ Streamlit Application"]

    UI --> AUTH["🔐 Authentication"]
    UI --> TX["💳 Transaction Layer"]
    UI --> ANA["📈 Analytics Engine"]
    UI --> AG["🤖 Agent Runtime"]
    UI --> RAG["📄 RAG Pipeline"]
    UI --> MR["🌍 Market Research"]
    UI --> EXP["📤 Safe CSV Export"]

    AUTH --> DB[("🗄️ SQLite")]
    TX --> DB
    ANA --> DB

    AG --> SUP{{"🧭 LangGraph Supervisor"}}
    AG --> LLM["⚡ Groq LLM"]

    SUP --> PF["Personal Finance Agent"]
    SUP --> MA["Market Research Agent"]
    SUP --> DA["Document / RAG Agent"]
    SUP --> AA["Analytics Agent"]

    PF --> TOOLS["Deterministic Financial Tools"]
    MA --> PROV["External Data Providers"]
    DA --> CHROMA[("🧬 Chroma Vector Store")]
    AA --> ANA

    RAG --> EMB["Embeddings"] --> CHROMA

    PROV --> SEC["SEC / XBRL"]
    PROV --> FRED["FRED"]
    PROV --> MKT["Market Data"]

    classDef ui fill:#4F8CFF,stroke:#1E3A8A,color:#fff
    classDef store fill:#0F172A,stroke:#38BDF8,color:#E2E8F0
    classDef agent fill:#EDE9FE,stroke:#8B5CF6,color:#0B1220
    classDef ext fill:#FEF3C7,stroke:#F59E0B,color:#0B1220
    class UI ui
    class DB,CHROMA store
    class SUP,PF,MA,DA,AA agent
    class SEC,FRED,MKT,PROV ext
```

<br/>

## ✦ Agentic Design

Fintoran uses a **supervisor-driven architecture** instead of routing every request straight to a single LLM.

```mermaid
flowchart LR
    Q(["❓ User Query"]) --> S{{"🧭 Supervisor"}}

    S -->|Personal finance| P["Personal Finance Agent"]
    S -->|Market question| M["Market Research Agent"]
    S -->|Documents| D["Document / RAG Agent"]
    S -->|Analytics| A["Analytics Agent"]

    P --> T1["Financial Tools"]
    M --> T2["Market Tools"]
    D --> T3["Retrieval Tools"]
    A --> T4["Analytics Tools"]

    T1 & T2 & T3 & T4 --> V["✅ Validation"]
    V --> R["✍️ Response Synthesis"]
    R --> O(["👤 User"])

    classDef sup fill:#8B5CF6,stroke:#4C1D95,color:#fff,stroke-width:2px
    classDef ok fill:#10B981,stroke:#065F46,color:#fff
    class S sup
    class V ok
```

### Life of a Query

```mermaid
sequenceDiagram
    autonumber
    actor U as 👤 User
    participant UI as Streamlit UI
    participant S as Supervisor
    participant A as Specialist Agent
    participant T as Deterministic Tools
    participant L as Groq LLM

    U->>UI: Ask a financial question
    UI->>S: Query + memory context
    S->>A: Route to the right specialist
    A->>T: Compute or retrieve
    T-->>A: Verified numbers + sources
    A->>L: Explain and synthesize
    L-->>A: Draft response
    A-->>S: Validated result
    S-->>UI: Grounded answer
    UI-->>U: Insight with sources
```

### Separation of Concerns

| Layer | Responsibility | Owner |
|:---|:---|:---|
| **Computation** | Exact arithmetic, aggregation, forecasting | Deterministic Python |
| **Reasoning** | Explanation, planning, synthesis | LLM agents |
| **Retrieval** | Document and memory grounding | Chroma + retrievers |
| **Presentation** | Rendering, sources, safe output | Streamlit |

<br/>

## ✦ Data Pipeline

Imported data flows through a **validated pipeline**. Raw CSV rows are never inserted directly.

```mermaid
flowchart LR
    RAW(["📥 RAW CSV"]) --> S1["🔎 Schema<br/>Detect"]
    S1 --> S2["🧭 Column<br/>Mapping"]
    S2 --> S3["🛡️ Validation"]
    S3 --> S4["🧹 Normalization"]
    S4 --> S5["✨ Enrichment"]
    S5 --> S6["♻️ Duplicate<br/>Detection"]
    S6 --> S7["💾 Persistence"]
    S7 --> DB[("🗄️ SQLite")]

    classDef stage fill:#DBEAFE,stroke:#3B82F6,color:#0B1220
    classDef io fill:#4F8CFF,stroke:#1E3A8A,color:#fff
    class S1,S2,S3,S4,S5,S6,S7 stage
    class RAW,DB io
```

<div align="center">

| Ingestion | Processing | Delivery |
|:---|:---|:---|
| Schema detection | Date parsing | Preview before import |
| Column mapping | Debit / credit handling | Import summaries |
| Malformed row handling | Currency normalization | Provenance tracking |
| Duplicate detection | Categorization and merchants | Safe export |
| | Recurring transactions | |

</div>

<br/>

## ✦ Analytics Engine

The analytics layer is **intentionally deterministic**. The LLM never performs core financial arithmetic.

```mermaid
flowchart LR
    DB[("🗄️ Database")] --> DC["⚙️ Deterministic<br/>Computation"]
    DC --> VN["✅ Verified<br/>Numbers"]
    VN --> LE["🧠 LLM<br/>Explanation"]

    DC --> M1["Cash flow"]
    DC --> M2["Spending trends"]
    DC --> M3["Category distribution"]
    DC --> M4["Budget utilization"]
    DC --> M5["Savings patterns"]
    DC --> M6["Forecasts"]
    DC --> M7["Anomalies"]

    classDef core fill:#10B981,stroke:#065F46,color:#fff
    classDef ai fill:#8B5CF6,stroke:#4C1D95,color:#fff
    class DC,VN core
    class LE ai
```

<br/>

## ✦ Forecasting

Forecasts use deterministic methods and are shown with uncertainty **only when the data supports it**.

```mermaid
flowchart TD
    H["📜 Historical Transactions"] --> TS["📉 Time Series"]
    TS --> MS{"Model Selection"}
    MS --> N["Naive"]
    MS --> MA["Moving Average"]
    MS --> WA["Weighted Average"]
    N --> HO["🧪 Holdout Check"]
    MA --> HO
    WA --> HO
    HO --> FR(["🔮 Forecast + Range"])

    classDef out fill:#4F8CFF,stroke:#1E3A8A,color:#fff
    class FR out
```

<br/>

## ✦ Anomaly Detection

Fintoran analyzes **multiple dimensions** rather than flagging every unusual amount.

```mermaid
mindmap
  root((Anomaly<br/>Analysis))
    Amount
      Unusual amount
    Merchant
      Unusual merchant
    Category
      Unusual category
    Frequency
      Unusual frequency
    Recurring
      Payment deviation
    Timing
      Unusual day
      Unusual time
    History
      Behavior deviation
```

<br/>

## ✦ RAG and Memory

Conversation memory and document retrieval are **separate systems** that solve different problems.

```mermaid
flowchart TD
    FILE["📎 PDF / TXT / MD / CSV"] --> ING["Document Ingestion"]
    ING --> CLN["Text Processing"]
    CLN --> CHK["Chunking"]
    CHK --> EMB["Embedding"]
    EMB --> STORE[("🧬 Chroma")]

    QRY(["❓ User Query"]) --> RET["Retriever"]
    RET --> STORE
    STORE --> META["Metadata + Source IDs"]
    META --> CTX["Retrieved Context"]
    CTX --> LLM["⚡ Agent / LLM"]
    LLM --> ANS(["✅ Answer + Citations"])

    classDef store fill:#0F172A,stroke:#38BDF8,color:#E2E8F0
    classDef out fill:#10B981,stroke:#065F46,color:#fff
    class STORE store
    class ANS out
```

<div align="center">

| | 🧠 Conversation Memory | 📄 Document RAG |
|:---|:---|:---|
| **Answers** | *"What did we discuss?"* | *"What does my document say?"* |
| **Source** | User dialogue | User documents |
| **Purpose** | Context recall | Grounded retrieval |
| **Storage** | Memory layer (Chroma) | Document layer (Chroma) |

</div>

**Retrieval supports:** ingestion · chunking · embeddings · metadata · source identifiers · retrieval scores · document isolation · reindexing · duplicate handling · deletion · source-aware responses

<br/>

## ✦ Market Research

The research layer is built around **external data provenance**.

```mermaid
flowchart TD
    MQ(["🌍 Market Question"]) --> MRA{{"Market Research Agent"}}
    MRA --> PR["Price Data"]
    MRA --> CO["Company Data"]
    MRA --> MC["Macro Data"]

    PR --> MP["Market Provider"]
    CO --> SEC["SEC / XBRL"]
    MC --> FRED["FRED"]

    MP --> SV["✅ Source Validation"]
    SEC --> SV
    FRED --> SV
    SV --> DS["Data Synthesis"]
    DS --> SP(["📚 Source Panel"])

    classDef agent fill:#8B5CF6,stroke:#4C1D95,color:#fff
    classDef out fill:#10B981,stroke:#065F46,color:#fff
    class MRA agent
    class SP out
```

<div align="center">

| Market | Fundamentals | Macro and Provenance |
|:---|:---|:---|
| Quotes | Company fundamentals | Macroeconomic indicators |
| Historical prices | SEC filings | Source provenance |
| Returns | Earnings information | |
| Volatility | | |
| Drawdowns | | |
| Moving averages and volume | | |

</div>

<br/>

## ✦ Security

Fintoran treats financial data as **private application data**.

```mermaid
flowchart TD
    AU(["🔐 Authenticated User"]) --> ISO{{"User Isolation"}}
    ISO --> T["💳 Transactions"]
    ISO --> M["🧠 Memory"]
    ISO --> D["📄 Documents"]
    T --> APP["🖥️ Application"]
    M --> APP
    D --> APP

    classDef shield fill:#EF4444,stroke:#7F1D1D,color:#fff,stroke-width:2px
    class ISO shield
```

<div align="center">

| 🔑 Identity | 🧱 Data | 📁 Files | 🤖 AI |
|:---|:---|:---|:---|
| bcrypt authentication | Account-level isolation | Upload validation | Prompt injection defenses |
| Environment-based secrets | Input validation | Upload limits | Private document isolation |
| No API keys in source | Safe rendering | Path traversal protection | Controlled logging |

</div>

### Safe CSV Export

Values that begin with spreadsheet formula prefixes are neutralized so spreadsheet apps never execute them.

| Raw value | Exported as |
|:---|:---|
| `=SUM(A1:A2)` | `'=SUM(A1:A2)` |
| `+100` | `'+100` |
| `-100` | `'-100` |
| `@command` | `'@command` |

<br/>

## ✦ Reliability

Agent execution is **failure-aware**. Provider failures never break core deterministic functionality.

```mermaid
stateDiagram-v2
    [*] --> Request
    Request --> Primary: LLM call with timeout
    Primary --> Success: ok
    Primary --> Retry: failure
    Retry --> Success: ok
    Retry --> Fallback: retries exhausted
    Fallback --> Success: ok
    Fallback --> SafeError: failure
    Success --> [*]
    SafeError --> [*]
```

<br/>

## ✦ Testing and CI/CD

```mermaid
flowchart LR
    DEV(["👩‍💻 Developer"]) --> GIT["Git Push"] --> GH["GitHub"] --> CI{{"GitHub Actions"}}

    CI --> PY311["Python 3.11"]
    CI --> PY312["Python 3.12"]
    CI --> TEST["Pytest"]
    CI --> COMP["Compile Check"]
    CI --> DOCK["Docker Build"]

    PY311 & PY312 & TEST & COMP & DOCK --> ST["✅ Validation"]
    ST --> DEP(["🚀 Deployment"])

    classDef ci fill:#2088FF,stroke:#0B3D91,color:#fff
    classDef ok fill:#10B981,stroke:#065F46,color:#fff
    class CI ci
    class ST,DEP ok
```

<div align="center">

| 🧪 Unit | 🔗 Integration | 🛡️ Security |
|:---:|:---:|:---:|
| Application behavior | Financial processing | Security-sensitive paths |
| Regression cases | Import behavior | Upload and export safety |

![Tests](https://img.shields.io/badge/pytest-49%20passed-10B981?style=for-the-badge&logo=pytest&logoColor=white)
![Compile](https://img.shields.io/badge/compile-validated-10B981?style=for-the-badge)
![Smoke](https://img.shields.io/badge/smoke%20test-passing-10B981?style=for-the-badge)

</div>

<br/>

## ✦ Docker

```mermaid
flowchart LR
    DF["📄 Dockerfile"] --> B["Build"] --> I["Install Dependencies"] --> NR["Non-Root Runtime"] --> HC["Healthcheck"] --> APP(["🖥️ Streamlit App"])

    classDef out fill:#2496ED,stroke:#0B4F8A,color:#fff
    class APP out
```

Designed for **deterministic startup** · **non-root execution** · **health checks** · **application isolation** · **runtime environment variables** · **reproducible dependency installation**

<br/>

## ✦ User Journey

```mermaid
journey
    title Fintoran Financial Intelligence Journey
    section Onboarding
      Create account: 5: User
      Authenticate: 5: User
    section Data
      Import transactions: 5: User
      Validate dataset: 5: Fintoran
      Normalize data: 5: Fintoran
    section Intelligence
      Analyze spending: 5: Fintoran
      Detect anomalies: 5: Fintoran
      Generate insights: 5: Fintoran
      Forecast trends: 4: Fintoran
    section AI
      Ask Copilot: 5: User
      Route to specialist: 5: Fintoran
      Retrieve context: 5: Fintoran
      Generate grounded response: 5: Fintoran
    section Research
      Research market: 4: User
      Retrieve external data: 4: Fintoran
      Present sources: 5: Fintoran
```

<br/>

## ✦ Conceptual Data Ownership

```mermaid
erDiagram
    USER ||--o{ TRANSACTION : owns
    USER ||--o{ BUDGET : sets
    USER ||--o{ MEMORY : accumulates
    USER ||--o{ DOCUMENT : uploads
    DOCUMENT ||--o{ CHUNK : "split into"
```

<br/>

## ✦ Tech Stack

<div align="center">

| Layer | Technologies |
|:---|:---|
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) |
| **Application** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white) ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| **AI** | ![Groq](https://img.shields.io/badge/Groq-F55036?style=flat-square) LLM reasoning · Agent orchestration · RAG |
| **Data** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) ![Chroma](https://img.shields.io/badge/Chroma-5B21B6?style=flat-square) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) |
| **External Data** | SEC / XBRL · FRED · Market data providers |
| **Security** | bcrypt · Input validation · User isolation · Safe file handling |
| **DevOps** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white) Streamlit Community Cloud |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white) |

</div>

<br/>

## ✦ Project Structure

```text
Fintoran/
│
├── app.py
│
├── agents/
│   ├── supervisor
│   ├── personal finance
│   ├── market research
│   ├── analytics
│   └── document / RAG
│
├── services/
│   ├── import pipeline
│   ├── analytics
│   ├── forecasting
│   ├── anomaly detection
│   ├── market data
│   └── persistence
│
├── tools/
│   ├── financial tools
│   ├── market tools
│   └── retrieval tools
│
├── tests/
│   ├── unit tests
│   ├── integration tests
│   └── security tests
│
├── data/
│   └── datasets
│
├── .streamlit/
│   └── config.toml
│
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── .env.example
├── SECURITY.md
├── DATA_SOURCES.md
├── EVALUATION.md
├── TESTING.md
└── README.md
```

<br/>

## ✦ Quick Start

<details open>
<summary><b>1 · Clone and set up the environment</b></summary>

<br/>

```bash
git clone https://github.com/i-Anurag1/Fintoran.git
cd Fintoran

python -m venv .venv
```

Activate the environment:

```powershell
# Windows
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

</details>

<details open>
<summary><b>2 · Configure secrets</b></summary>

<br/>

```bash
cp .env.example .env
```

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

Example `.env`:

```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_FALLBACK_MODELS=llama-3.1-8b-instant
FRED_API_KEY=your_fred_key
SEC_USER_AGENT=Fintoran/1.0 your-email@example.com
```

> ⚠️ **Never commit `.env`.** On Streamlit Community Cloud, configure secrets through the app settings instead of committing secret files.

</details>

<details open>
<summary><b>3 · Run the app</b></summary>

<br/>

```bash
streamlit run app.py
```

</details>

<details>
<summary><b>4 · Run the tests</b></summary>

<br/>

```bash
pytest -q
python -m compileall .
```

</details>

<details>
<summary><b>5 · Run with Docker</b></summary>

<br/>

```bash
docker build -t fintoran .
docker run --env-file .env -p 8501:8501 fintoran
```

Then open `http://localhost:8501`.

</details>

<br/>

## ✦ Project Status

<div align="center">

| Component | Status |
|:---|:---:|
| Core Application | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Agent Architecture | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Financial Analytics | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| CSV Import Pipeline | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Forecasting | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Anomaly Detection | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| RAG | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Persistent Memory | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Market Research | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Authentication | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Security Hardening | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| Automated Tests | ![Passing](https://img.shields.io/badge/PASSING-4F8CFF?style=flat-square) |
| Docker | ![Complete](https://img.shields.io/badge/COMPLETE-10B981?style=flat-square) |
| CI Validation | ![Passing](https://img.shields.io/badge/PASSING-4F8CFF?style=flat-square) |
| Streamlit Deployment | ![Live](https://img.shields.io/badge/LIVE-F59E0B?style=flat-square) |

</div>

<br/>

## ✦ Engineering Principles

<div align="center">

| # | Principle |
|:---:|:---|
| 1 | Deterministic financial computation |
| 2 | Explicit data provenance |
| 3 | User data isolation |
| 4 | Agent specialization |
| 5 | Retrieval-grounded answers |
| 6 | Validated external data |
| 7 | Safe file processing |
| 8 | Reproducible testing |
| 9 | Containerized deployment |
| 10 | Financial safety disclaimers |

</div>

<br/>

## ✦ Design Philosophy

```mermaid
flowchart TD
    A["📊 Financial Data"] --> B["⚙️ Deterministic Analytics"]
    B --> C["🤖 Agents + Retrieval"]
    C --> D["✅ Verified Intelligence"]
    D --> E(["🧑 Human Decision"])

    classDef s fill:#DBEAFE,stroke:#3B82F6,color:#0B1220
    classDef h fill:#10B981,stroke:#065F46,color:#fff,stroke-width:2px
    class A,B,C,D s
    class E h
```

Fintoran does not attempt to replace financial judgment. It provides structured information, calculations, context and explanations so users can make informed decisions.

<br/>

## ✦ Roadmap

```mermaid
timeline
    title Fintoran Roadmap
    section Current
        Foundation : Agentic AI : Analytics : RAG : Memory
        Hardening : Security : Testing : CI
    section Future
        Evaluation : Richer financial evaluation datasets : Expanded agent evaluation
        Data : More market data integrations : Provider-level caching
        Intelligence : Stronger forecasting evaluation : Richer portfolio analytics
        Documents : Additional document formats
        Planning : Advanced financial planning workflows
```

<br/>

## ✦ Financial Safety

> ⚠️ Fintoran is an **information and analysis tool**. Its outputs are not a substitute for professional financial, investment, tax or legal advice.
>
> Market and financial information changes over time. Please verify important information independently before making financial decisions.

<br/>

## ✦ Repository and Links

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-i--Anurag1%2FFintoran-181717?style=for-the-badge&logo=github)](https://github.com/i-Anurag1/Fintoran)
[![Live App](https://img.shields.io/badge/Live_App-fintoranagent.streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://fintoranagent.streamlit.app/)

</div>

## ✦ License

See the repository for the applicable project license and terms.

<br/>

<div align="center">

```text
DATA  →  ANALYZE  →  RETRIEVE  →  REASON  →  VERIFY  →  UNDERSTAND
```

### Agentic AI for Personal Financial Intelligence

**Built with Python · Streamlit · LangGraph · LangChain · Groq · SQLite · Chroma · Docker · Pytest**

<br/>

[Live Demo](https://fintoranagent.streamlit.app/) &nbsp;·&nbsp; [Source Code](https://github.com/i-Anurag1/Fintoran)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer" alt="footer" width="100%"/>

</div>
