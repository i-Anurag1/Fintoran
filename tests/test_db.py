def test_create_and_fetch_user(temp_db):
    user_id = temp_db.create_user("bob", "hashed_pw")
    user = temp_db.get_user_by_id(user_id)
    assert user["username"] == "bob"

    by_name = temp_db.get_user_by_username("bob")
    assert by_name["id"] == user_id


def test_duplicate_username_raises(temp_db):
    import sqlite3
    temp_db.create_user("bob", "hash1")
    try:
        temp_db.create_user("bob", "hash2")
        assert False, "expected IntegrityError"
    except sqlite3.IntegrityError:
        pass


def test_transactions_are_scoped_per_user(temp_db):
    user_a = temp_db.create_user("alice", "h")
    user_b = temp_db.create_user("bob", "h")

    temp_db.insert_transactions(user_a, [
        {"date": "2024-01-01", "description": "Coffee", "amount": -100,
         "type": "debit", "category": "Food", "is_recurring": 0, "is_anomaly": 0},
    ])
    temp_db.insert_transactions(user_b, [
        {"date": "2024-01-02", "description": "Rent", "amount": -20000,
         "type": "debit", "category": "Rent", "is_recurring": 0, "is_anomaly": 0},
    ])

    a_txns = temp_db.get_all_transactions(user_a)
    b_txns = temp_db.get_all_transactions(user_b)

    assert len(a_txns) == 1 and a_txns[0]["description"] == "Coffee"
    assert len(b_txns) == 1 and b_txns[0]["description"] == "Rent"


def test_clear_transactions_only_affects_that_user(temp_db):
    user_a = temp_db.create_user("alice", "h")
    user_b = temp_db.create_user("bob", "h")
    row = {"date": "2024-01-01", "description": "X", "amount": -1,
           "type": "debit", "category": "Other", "is_recurring": 0, "is_anomaly": 0}
    temp_db.insert_transactions(user_a, [row])
    temp_db.insert_transactions(user_b, [row])

    temp_db.clear_transactions(user_a)

    assert temp_db.get_all_transactions(user_a) == []
    assert len(temp_db.get_all_transactions(user_b)) == 1


def test_budgets_scoped_per_user_and_upsert(temp_db):
    user_a = temp_db.create_user("alice", "h")
    user_b = temp_db.create_user("bob", "h")

    temp_db.set_budget(user_a, "Food & Dining", 5000)
    temp_db.set_budget(user_b, "Food & Dining", 9000)
    temp_db.set_budget(user_a, "Food & Dining", 6000)  # update

    assert temp_db.get_budgets(user_a) == {"Food & Dining": 6000}
    assert temp_db.get_budgets(user_b) == {"Food & Dining": 9000}
