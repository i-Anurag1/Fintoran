"""
Finance Tools
=============
The agent's capabilities over a user's personal transaction data. Every
function is scoped by user_id so one deployment can safely serve multiple
users with fully isolated data.

These are wrapped as LangChain tools per-user in core/agents.py — this file
stays framework-agnostic and just executes deterministic financial logic.
"""
import datetime
import calendar
import statistics
from collections import Counter
from database import db

CATEGORY_KEYWORDS = {
    "Food & Dining": ["swiggy", "zomato", "restaurant", "starbucks", "dinner", "cafe", "dominos", "coffee day"],
    "Groceries": ["bigbasket", "grocery", "supermarket", "dmart"],
    "Subscriptions": ["netflix", "spotify", "prime", "subscription", "gym", "cult fit", "youtube premium", "gaming subscription"],
    "Transport": ["uber", "ola", "petrol", "fuel", "hp pump", "metro card"],
    "Bills & Utilities": ["electricity", "bescom", "water", "bwssb", "mobile recharge", "jio", "airtel", "broadband", "fibernet", "gas cylinder"],
    "Shopping": ["amazon", "flipkart", "myntra", "shopping", "ikea", "apple store", "laptop purchase"],
    "Rent": ["rent"],
    "Healthcare": ["pharmacy", "medical", "apollo", "hospital", "health insurance"],
    "Entertainment": ["movie", "pvr", "bookmyshow"],
    "Investments": ["sip", "mutual fund", "zerodha", "stock", "groww", "ppf"],
    "Credit Card": ["credit card bill"],
    "Education": ["udemy", "book purchase", "course"],
    "Travel": ["flight booking", "makemytrip", "hotel booking"],
    "Income": ["salary", "freelance", "credit received", "income", "interest credit", "cashback"],
}


def _categorize(description: str) -> str:
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc for kw in keywords):
            return category
    return "Other"


def load_and_categorize_statement(user_id: int, csv_path: str) -> dict:
    """Parses a CSV bank statement, categorizes every transaction, detects
    recurring payments, and stores everything in the database under this
    user's account.

    If the CSV already has a 'category' column (e.g. from a dataset that
    ships with its own labels), that's used directly — keyword-based
    categorization only kicks in when descriptions are real merchant text
    to match against. This matters for anonymized/synthetic datasets where
    descriptions are meaningless placeholder text."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"date", "description", "amount", "type"}
    missing = required - set(df.columns)
    if missing:
        return {"status": "error", "error": f"CSV missing required column(s): {', '.join(sorted(missing))}"}

    if "category" in df.columns and df["category"].notna().any():
        df["category"] = df["category"].fillna("Other")
    else:
        df["category"] = df["description"].apply(_categorize)

    counts = Counter(df["description"])
    df["is_recurring"] = df["description"].apply(lambda d: 1 if counts[d] >= 2 else 0)
    df["is_anomaly"] = 0
    df["user_id"] = user_id

    db.clear_transactions(user_id)
    db.insert_transactions(user_id, df.to_dict(orient="records"))
    return {"status": "success", "transactions_loaded": len(df)}


def get_transaction_summary(user_id: int, category: str = None, current_month_only: bool = False) -> dict:
    """Returns total spend, income, and a category-wise breakdown. Optionally
    filter to a single category and/or restrict to just the most recent
    calendar month in the data (useful for "this month" style questions,
    as opposed to all-time totals)."""
    transactions = db.get_all_transactions(user_id)

    if current_month_only and transactions:
        latest_date = max(datetime.date.fromisoformat(t["date"][:10]) for t in transactions)
        transactions = [
            t for t in transactions
            if datetime.date.fromisoformat(t["date"][:10]).year == latest_date.year
            and datetime.date.fromisoformat(t["date"][:10]).month == latest_date.month
        ]

    if category:
        transactions = [t for t in transactions if t["category"].lower() == category.lower()]

    spend = {}
    total_income = 0
    for t in transactions:
        if t["type"] == "debit":
            spend[t["category"]] = spend.get(t["category"], 0) + abs(t["amount"])
        else:
            total_income += t["amount"]

    return {
        "period": "current_month" if current_month_only else "all_time_in_dataset",
        "total_spent": round(sum(spend.values()), 2),
        "total_income": round(total_income, 2),
        "by_category": {k: round(v, 2) for k, v in spend.items()},
        "transaction_count": len(transactions),
    }


def check_budget_status(user_id: int, category: str, monthly_limit: float) -> dict:
    """Compares actual spend in a category, for the current month only,
    against a given monthly limit."""
    transactions = db.get_all_transactions(user_id)
    if not transactions:
        return {"error": "No transactions loaded yet."}

    latest_date = max(datetime.date.fromisoformat(t["date"][:10]) for t in transactions)
    spent = sum(
        abs(t["amount"]) for t in transactions
        if t["type"] == "debit"
        and t["category"].lower() == category.lower()
        and datetime.date.fromisoformat(t["date"][:10]).year == latest_date.year
        and datetime.date.fromisoformat(t["date"][:10]).month == latest_date.month
    )
    return {
        "category": category,
        "limit": monthly_limit,
        "spent_this_month": round(spent, 2),
        "remaining": round(monthly_limit - spent, 2),
        "over_budget": spent > monthly_limit,
        "pct_used": round((spent / monthly_limit) * 100, 1) if monthly_limit else 0,
    }


def forecast_month_end_balance(user_id: int, current_balance: float) -> dict:
    """Projects end-of-month balance using average daily spend run-rate for
    the CURRENT month only, anchored to the latest transaction date in the
    data (so it works correctly with multi-month historical datasets, not
    just live single-month data)."""
    transactions = db.get_all_transactions(user_id)
    if not transactions:
        return {"error": "No transactions loaded yet."}

    latest_date = max(datetime.date.fromisoformat(t["date"][:10]) for t in transactions)
    days_in_month = calendar.monthrange(latest_date.year, latest_date.month)[1]
    day_of_month = latest_date.day

    current_month_txns = [
        t for t in transactions
        if datetime.date.fromisoformat(t["date"][:10]).year == latest_date.year
        and datetime.date.fromisoformat(t["date"][:10]).month == latest_date.month
    ]
    total_spent = sum(abs(t["amount"]) for t in current_month_txns if t["type"] == "debit")
    avg_daily_spend = total_spent / max(day_of_month, 1)
    days_left = days_in_month - day_of_month
    projected_spend = avg_daily_spend * days_left
    projected_balance = current_balance - projected_spend

    return {
        "current_balance": current_balance,
        "avg_daily_spend": round(avg_daily_spend, 2),
        "days_left_in_month": days_left,
        "projected_additional_spend": round(projected_spend, 2),
        "projected_month_end_balance": round(projected_balance, 2),
    }


def check_can_afford(user_id: int, amount: float, current_balance: float) -> dict:
    """Determines whether a hypothetical purchase is affordable given the
    month-end forecast, with a verdict and reasoning trail."""
    forecast = forecast_month_end_balance(user_id, current_balance)
    if "error" in forecast:
        return forecast

    balance_after = forecast["projected_month_end_balance"] - amount
    if balance_after > 0:
        verdict = "affordable"
    elif balance_after > -0.15 * current_balance:
        verdict = "tight_but_possible"
    else:
        verdict = "not_recommended"

    return {
        "purchase_amount": amount,
        "verdict": verdict,
        "projected_balance_before_purchase": forecast["projected_month_end_balance"],
        "projected_balance_after_purchase": round(balance_after, 2),
    }


def detect_spending_anomalies(user_id: int, z_threshold: float = 2.0) -> dict:
    """Flags transactions that are statistical outliers vs. the user's own
    spending history (z-score based)."""
    transactions = db.get_all_transactions(user_id)
    debits = [abs(t["amount"]) for t in transactions if t["type"] == "debit"]
    if len(debits) < 3:
        return {"anomalies": []}

    mean = statistics.mean(debits)
    stdev = statistics.stdev(debits) or 1e-6

    anomalies = []
    for t in transactions:
        if t["type"] != "debit":
            continue
        z = (abs(t["amount"]) - mean) / stdev
        if z >= z_threshold:
            anomalies.append({
                "date": t["date"], "description": t["description"],
                "amount": abs(t["amount"]), "z_score": round(z, 2),
            })
    return {"anomalies": anomalies, "mean_transaction": round(mean, 2), "stdev": round(stdev, 2)}


def get_recurring_payments(user_id: int) -> dict:
    """Lists all detected recurring/subscription-like payments."""
    transactions = db.get_all_transactions(user_id)
    recurring = [t for t in transactions if t.get("is_recurring") and t["type"] == "debit"]
    seen = {}
    for t in recurring:
        seen[t["description"]] = abs(t["amount"])
    return {"recurring_payments": [{"description": k, "amount": v} for k, v in seen.items()]}
