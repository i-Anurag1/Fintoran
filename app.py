"""
Financial Agent — Agentic AI
Run with: streamlit run app.py
"""
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from database import db
from auth import auth
from memory.vector_memory import ConversationMemory
from tools.finance_tools import load_and_categorize_statement, get_transaction_summary
from core.graph import MultiAgentOrchestrator

# All file paths are resolved relative to this file, not the process's
# current working directory. Launching `streamlit run app.py` from a
# different folder (a different machine, a different shell, a desktop
# shortcut, a systemd service, etc.) previously broke dataset loading and
# uploads — this fixes that class of "works on my laptop only" bug.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, ".env"))

st.set_page_config(page_title="Financial Agent", page_icon=":bar_chart:", layout="wide")

# ---------------- Light, professional visual polish ----------------
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px;}
    h1, h2, h3 {font-weight: 600; letter-spacing: -0.01em;}
    .stButton>button {border-radius: 8px; font-weight: 500;}
    .stTabs [data-baseweb="tab"] {font-weight: 500;}
    div[data-testid="stMetric"] {
        background: #F4F6F8; border: 1px solid #E5E9EF;
        border-radius: 10px; padding: 12px 16px;
    }
    div[data-testid="stChatMessage"] {border-radius: 10px;}
    .app-caption {color: #5B6472; font-size: 0.92rem;}
    @media (max-width: 640px) {
        .block-container {padding-left: 1rem; padding-right: 1rem;}
    }
</style>
""", unsafe_allow_html=True)

db.init_db()

# ---------------- Session state ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False


def _login_screen():
    st.title("Financial Agent")
    st.markdown(
        '<p class="app-caption">A multi-agent personal finance assistant with persistent memory. '
        "Sign in or create an account to continue — your data stays private to your account.</p>",
        unsafe_allow_html=True,
    )
    st.info(
        "Signing in only affects this browser/device. If you use the app on your phone and "
        "your laptop, sign in on each — your account, transactions, and memory are shared and "
        "identical either way."
    )

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in", use_container_width=True)
        if submitted:
            result = auth.login(username, password)
            if result["success"]:
                st.session_state.user = result["user"]
                st.rerun()
            else:
                st.error(result["message"])

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Choose a username", key="signup_username")
            new_password = st.text_input("Choose a password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if new_password != confirm_password:
                st.error("Passwords don't match.")
            else:
                result = auth.signup(new_username, new_password)
                if result["success"]:
                    st.session_state.user = result["user"]
                    st.success("Account created — you're logged in.")
                    st.rerun()
                else:
                    st.error(result["message"])


if st.session_state.user is None:
    _login_screen()
    st.stop()

user = st.session_state.user
user_id = user["id"]

if "agent" not in st.session_state:
    st.session_state.agent = MultiAgentOrchestrator()
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(user_id)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(f"**Signed in as** {user['username']}")
    if st.button("Log out", use_container_width=True):
        st.session_state.user = None
        st.session_state.chat_history = []
        st.session_state.data_loaded = False
        for key in ("agent", "memory"):
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.subheader("Setup")
    if st.session_state.agent.is_configured():
        st.success("Groq API key configured")
    else:
        st.warning("Groq API key not set")
        st.caption("Set `GROQ_API_KEY` in a `.env` file to activate the agent. Free tier at console.groq.com")

    st.divider()
    current_balance = st.number_input(
        "Current account balance (₹)", min_value=0.0, value=25000.0, step=500.0
    )
    st.session_state["current_balance"] = current_balance

    st.divider()
    st.subheader("Load transactions")
    uploaded = st.file_uploader("Upload your own bank statement (CSV)", type=["csv"])
    use_kaggle = st.button("Load Kaggle dataset (1,500 txns, 5 yrs)", use_container_width=True)
    use_synthetic = st.button("Load synthetic test data", use_container_width=True)

    if uploaded is not None:
        upload_path = os.path.join(DATA_DIR, f"_uploaded_{user_id}.csv")
        with open(upload_path, "wb") as f:
            f.write(uploaded.getvalue())
        result = load_and_categorize_statement(user_id, upload_path)
        if result.get("status") == "error":
            st.error(result["error"])
        else:
            st.session_state.data_loaded = True
            st.success(f"Loaded {result['transactions_loaded']} transactions")
    elif use_kaggle:
        result = load_and_categorize_statement(user_id, os.path.join(DATA_DIR, "kaggle_transactions.csv"))
        st.session_state.data_loaded = True
        st.success(f"Loaded {result['transactions_loaded']} real transactions (Kaggle)")
    elif use_synthetic:
        result = load_and_categorize_statement(user_id, os.path.join(DATA_DIR, "sample_transactions.csv"))
        st.session_state.data_loaded = True
        st.success(f"Loaded {result['transactions_loaded']} synthetic transactions")

    st.divider()
    st.subheader("Memory")
    st.caption(
        "The agent remembers past conversations and preferences across "
        "sessions, per account, using a persistent vector store."
    )
    if st.button("Forget everything", use_container_width=True):
        st.session_state.memory.clear()
        st.success("Memory cleared for this account.")

    st.divider()
    with st.expander("About this agent"):
        st.caption(
            "Not a rule-based chatbot. A Supervisor agent routes each question "
            "to specialist sub-agents (Budget Agent, Market Agent) which decide "
            "for themselves which tools to call. Open 'Reasoning trace' below "
            "the chat to see the handoffs happen."
        )

# ---------------- Main area ----------------
if not st.session_state.data_loaded:
    existing = db.get_all_transactions(user_id)
    if existing:
        st.session_state.data_loaded = True

if not st.session_state.data_loaded:
    st.info("Load transactions from the sidebar to get started — or just chat, market questions work without data too.")

tab_chat, tab_data, tab_about = st.tabs(["Chat", "Transaction data", "How it works"])

with tab_chat:
    st.subheader("Ask anything")
    st.markdown(
        '<p class="app-caption">Try: "Can I afford a ₹15,000 phone this month?" · '
        '"What\'s TCS.NS trading at?" · "Am I overspending on food?" · '
        '"Should I buy AAPL or pay off my credit card?"</p>',
        unsafe_allow_html=True,
    )

    for turn in st.session_state.chat_history:
        with st.chat_message(turn["role"]):
            st.write(turn["content"])

    user_input = st.chat_input("Ask the financial agent...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking through your question..."):
                history_for_agent = [
                    {"role": t["role"], "content": t["content"]}
                    for t in st.session_state.chat_history[:-1]
                ]
                memory_context = st.session_state.memory.get_context_string(user_input)
                result = st.session_state.agent.run(
                    user_id, user_input, history_for_agent, memory_context
                )
            st.write(result["answer"])
            st.session_state["last_trace"] = result["trace"]

        st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
        st.session_state.memory.add_chat_turn("user", user_input)
        st.session_state.memory.add_chat_turn("assistant", result["answer"])

    trace = st.session_state.get("last_trace", [])
    with st.expander("Reasoning trace", expanded=False):
        st.caption("Supervisor routing and specialist agent handoffs for the last question.")
        if trace:
            for step in trace:
                st.text(step)
        else:
            st.caption("Ask a question to see the agent's reasoning steps here.")

with tab_data:
    st.subheader("Loaded transactions")
    if st.session_state.data_loaded:
        transactions = db.get_all_transactions(user_id)
        df = pd.DataFrame(transactions)
        st.dataframe(df, use_container_width=True, hide_index=True)

        summary = get_transaction_summary(user_id)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total spent", f"₹{summary['total_spent']:,.0f}")
        col2.metric("Total income", f"₹{summary['total_income']:,.0f}")
        col3.metric("Transactions", summary["transaction_count"])

        if summary["by_category"]:
            chart_df = pd.DataFrame(list(summary["by_category"].items()), columns=["Category", "Amount"])
            st.bar_chart(chart_df.set_index("Category"))
    else:
        st.info("No data loaded yet — use the sidebar.")

with tab_about:
    st.subheader("What makes this 'agentic'?")
    st.markdown("""
Most finance dashboards are **pipelines**: fixed steps that always run in the same order.
This project is a **multi-agent system**: a Supervisor agent decides which specialist
agent(s) should handle each question, and each specialist decides for itself which tools
to call.

**Concretely:**
- A **Supervisor** (`core/graph.py`, built with LangGraph) reads your question and routes
  it to the **Budget Agent** (personal transactions, budgets, forecasts, affordability,
  anomalies, recurring bills) and/or the **Market Agent** (live stock prices, analyst
  recommendations, news) — nobody hardcoded "if user says 'stock', call get_stock_price".
- The Supervisor can chain agents: e.g. for "should I buy AAPL or pay off my card?" it
  might call the Market Agent for the price, then the Budget Agent for affordability,
  then synthesize one answer across both — a genuinely multi-step, multi-agent decision.
- Each specialist runs its own internal tool-calling loop within its domain.
- The agent has **persistent memory** (a per-account vector store) so it can recall past
  conversations and preferences across sessions, not just within one browser tab.
- Every routing decision and handoff is logged in the **Reasoning trace** panel under Chat.

**Tech stack:** Groq (Llama 3.3 70B) for fast, free-tier LLM inference · LangChain/LangGraph
for the supervisor/multi-agent graph · Chroma for persistent semantic memory · bcrypt for
auth · yfinance for live market data · DuckDuckGo (via `ddgs`) for news search · Streamlit
for the UI · SQLite for transaction/user storage.
    """)
