import pytest
from tools import finance_tools


def _load_fixture_transactions(temp_db, user_id):
    rows = [
        {"date": "2024-03-01", "description": "Salary", "amount": 50000,
         "type": "credit", "category": "Income", "is_recurring": 1, "is_anomaly": 0},
        {"date": "2024-03-02", "description": "Swiggy order", "amount": -450,
         "type": "debit", "category": "Food & Dining", "is_recurring": 0, "is_anomaly": 0},
        {"date": "2024-03-03", "description": "Netflix", "amount": -500,
         "type": "debit", "category": "Subscriptions", "is_recurring": 1, "is_anomaly": 0},
        {"date": "2024-03-10", "description": "Netflix", "amount": -500,
         "type": "debit", "category": "Subscriptions", "is_recurring": 1, "is_anomaly": 0},
        {"date": "2024-03-15", "description": "Laptop purchase", "amount": -80000,
         "type": "debit", "category": "Shopping", "is_recurring": 0, "is_anomaly": 0},
    ]
    temp_db.insert_transactions(user_id, rows)


def test_categorize_keyword_matching():
    assert finance_tools._categorize("Swiggy order #123") == "Food & Dining"
    assert finance_tools._categorize("Totally unknown merchant xyz") == "Other"


def test_transaction_summary_totals(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    summary = finance_tools.get_transaction_summary(sample_user["id"])

    assert summary["total_income"] == 50000
    assert summary["total_spent"] == 450 + 500 + 500 + 80000
    assert summary["transaction_count"] == 5


def test_transaction_summary_category_filter(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    summary = finance_tools.get_transaction_summary(sample_user["id"], category="Subscriptions")
    assert summary["total_spent"] == 1000


def test_transactions_scoped_to_user(temp_db, sample_user):
    other = temp_db.create_user("other_user", "h")
    _load_fixture_transactions(temp_db, sample_user["id"])
    summary = finance_tools.get_transaction_summary(other)
    assert summary["transaction_count"] == 0


def test_check_budget_status_over_and_under(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    over = finance_tools.check_budget_status(sample_user["id"], "Subscriptions", 500)
    assert over["over_budget"] is True

    under = finance_tools.check_budget_status(sample_user["id"], "Food & Dining", 1000)
    assert under["over_budget"] is False


def test_check_budget_status_no_data():
    result = finance_tools.check_budget_status(9999, "Food & Dining", 1000)
    assert "error" in result


def test_forecast_month_end_balance(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    forecast = finance_tools.forecast_month_end_balance(sample_user["id"], 100000)
    assert "projected_month_end_balance" in forecast
    assert forecast["days_left_in_month"] >= 0


def test_check_can_afford_verdicts(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    cheap = finance_tools.check_can_afford(sample_user["id"], 10, 1000000)
    assert cheap["verdict"] == "affordable"

    expensive = finance_tools.check_can_afford(sample_user["id"], 10_000_000, 100)
    assert expensive["verdict"] == "not_recommended"


def test_detect_spending_anomalies_flags_outlier(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    result = finance_tools.detect_spending_anomalies(sample_user["id"], z_threshold=1.0)
    flagged_descriptions = [a["description"] for a in result["anomalies"]]
    assert "Laptop purchase" in flagged_descriptions


def test_get_recurring_payments(temp_db, sample_user):
    _load_fixture_transactions(temp_db, sample_user["id"])
    result = finance_tools.get_recurring_payments(sample_user["id"])
    descriptions = [p["description"] for p in result["recurring_payments"]]
    assert "Netflix" in descriptions
    assert "Laptop purchase" not in descriptions
