from auth import auth


def test_password_hash_roundtrip():
    h = auth.hash_password("supersecret1")
    assert h != "supersecret1"
    assert auth.verify_password("supersecret1", h)
    assert not auth.verify_password("wrongpassword", h)


def test_signup_rejects_short_password(temp_db):
    result = auth.signup("newuser", "short")
    assert not result["success"]
    assert "8 characters" in result["message"]


def test_signup_rejects_invalid_username(temp_db):
    result = auth.signup("a", "longenoughpassword")
    assert not result["success"]


def test_signup_then_login_success(temp_db):
    signup_result = auth.signup("carol", "longenoughpassword")
    assert signup_result["success"]

    login_result = auth.login("carol", "longenoughpassword")
    assert login_result["success"]
    assert login_result["user"]["username"] == "carol"


def test_login_wrong_password_fails(temp_db):
    auth.signup("dave", "correctpassword1")
    result = auth.login("dave", "wrongpassword1")
    assert not result["success"]


def test_login_unknown_user_fails(temp_db):
    result = auth.login("ghost", "whatever123")
    assert not result["success"]


def test_signup_duplicate_username_fails(temp_db):
    first = auth.signup("erin", "firstpassword1")
    assert first["success"]
    second = auth.signup("erin", "secondpassword1")
    assert not second["success"]
    assert "already taken" in second["message"]
