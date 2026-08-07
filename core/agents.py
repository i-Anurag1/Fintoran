"""
Specialist Sub-Agents
=====================
Each sub-agent owns one domain and its own tool set, and reasons
independently within that domain (its own ReAct tool-calling loop). The
Supervisor (see core/graph.py) decides which sub-agent(s) to call and in
what order — this is the multi-agent handoff at the heart of this project.

  - Budget Agent  -> tools/finance_tools.py  (personal transactions, budgets,
                      forecasts, affordability, anomalies, recurring bills)
  - Market Agent  -> tools/market_tools.py   (live stock prices, analyst
                      recommendations, financial news)

Finance tools need to be scoped to the current user (so User A never sees
User B's transactions), so they're built per-request as closures over
user_id rather than being module-level constants like the market tools.

Agent construction uses `langchain.agents.create_agent` (the stable,
LangChain 1.0+ way to build a ReAct-style tool-calling agent). The old
`langgraph.prebuilt.create_react_agent` is kept as an automatic fallback
so this still runs against slightly older pinned environments.
"""
from langchain_core.tools import tool

try:
    from langchain.agents import create_agent as _create_agent

    def _build_react_agent(llm, tools, system_prompt):
        return _create_agent(model=llm, tools=tools, system_prompt=system_prompt)
except ImportError:  # pragma: no cover - fallback for pre-1.0 langchain/langgraph
    from langgraph.prebuilt import create_react_agent as _create_react_agent

    def _build_react_agent(llm, tools, system_prompt):
        return _create_react_agent(llm, tools, prompt=system_prompt)

from tools import finance_tools, market_tools

BUDGET_AGENT_PROMPT = (
    "You are the Budget Agent, a specialist in this user's personal finances. "
    "You have tools for transaction summaries, budget checks, month-end "
    "forecasting, affordability checks, anomaly detection, and recurring "
    "payments. Always ground numeric claims in tool results — never guess a "
    "number. If a tool returns an error (e.g. no data loaded), say so plainly. "
    "Answer only the personal-finance part of the task; be concise."
)

MARKET_AGENT_PROMPT = (
    "You are the Market Agent, a specialist in live market data. You have "
    "tools for live stock prices, analyst recommendations, and financial news "
    "search. Always ground numeric claims in tool results — never guess a "
    "price. If a tool returns an error, say so plainly. Answer only the "
    "market-data part of the task; be concise."
)


def _build_finance_tools(user_id: int):
    """Wraps tools/finance_tools.py functions as LangChain tools, closing
    over user_id so the LLM never has to (and can't) supply it."""

    @tool
    def get_transaction_summary(category: str = None, current_month_only: bool = False) -> dict:
        """Get total spend, income, and category-wise breakdown from the
        user's loaded transactions. Use for any question about how much the
        user spent, earned, or their spending breakdown."""
        return finance_tools.get_transaction_summary(user_id, category, current_month_only)

    @tool
    def check_budget_status(category: str, monthly_limit: float) -> dict:
        """Check actual spend in a category against a monthly budget limit.
        Use when the user asks if they're on/over budget for something."""
        return finance_tools.check_budget_status(user_id, category, monthly_limit)

    @tool
    def forecast_month_end_balance(current_balance: float) -> dict:
        """Projects the user's account balance at month end based on current
        spending rate. Use for questions about future balance or savings
        trajectory."""
        return finance_tools.forecast_month_end_balance(user_id, current_balance)

    @tool
    def check_can_afford(amount: float, current_balance: float) -> dict:
        """Determines if the user can afford a hypothetical purchase this
        month. Use for 'can I afford X' / 'should I buy X' questions."""
        return finance_tools.check_can_afford(user_id, amount, current_balance)

    @tool
    def detect_spending_anomalies(z_threshold: float = 2.0) -> dict:
        """Finds unusually large transactions vs. the user's normal pattern
        (statistical outliers). Use for suspicious/unusual charge questions."""
        return finance_tools.detect_spending_anomalies(user_id, z_threshold)

    @tool
    def get_recurring_payments() -> dict:
        """Lists subscriptions and recurring bills detected in the user's
        transactions."""
        return finance_tools.get_recurring_payments(user_id)

    return [
        get_transaction_summary,
        check_budget_status,
        forecast_month_end_balance,
        check_can_afford,
        detect_spending_anomalies,
        get_recurring_payments,
    ]


def _build_market_tools():
    """Wraps tools/market_tools.py — no user scoping needed, live market
    data is the same for everyone."""

    @tool
    def get_stock_price(ticker: str) -> dict:
        """Gets the current live price of a stock given its ticker symbol,
        e.g. 'AAPL', 'TCS.NS'."""
        return market_tools.get_stock_price(ticker)

    @tool
    def get_analyst_recommendations(ticker: str) -> dict:
        """Gets analyst buy/sell/hold recommendation summary for a stock."""
        return market_tools.get_analyst_recommendations(ticker)

    @tool
    def search_financial_news(query: str, max_results: int = 5) -> dict:
        """Searches the web for recent financial news on a company, stock,
        or economic topic."""
        return market_tools.search_financial_news(query, max_results)

    return [get_stock_price, get_analyst_recommendations, search_financial_news]


def build_budget_agent(llm, user_id: int):
    tools = _build_finance_tools(user_id)
    return _build_react_agent(llm, tools, BUDGET_AGENT_PROMPT)


def build_market_agent(llm):
    tools = _build_market_tools()
    return _build_react_agent(llm, tools, MARKET_AGENT_PROMPT)
