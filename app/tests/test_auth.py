import re
from werkzeug.security import generate_password_hash
import sqlite3

def _user_exists(app, email):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        return con.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone() is not None

def _first_user_type_value(signup_html: str):
    # Find: <input ... name="user_type" value="SOMETHING">
    m = re.findall(r'<input[^>]*name="user_type"[^>]*value="([^"]+)"', signup_html)
    return m[0] if m else None

def test_signup_form_renders(client):
    r = client.get("/signup")
    assert r.status_code == 200
    assert b"Sign Up" in r.data

def test_signup_success(app, client):
    get_r = client.get("/signup")
    assert get_r.status_code == 200
    user_type_val = _first_user_type_value(get_r.data.decode())
    assert user_type_val
    email = "new@example.com"
    assert not _user_exists(app, email)

    payload = {
        "email": email,
        "first_name": "New",
        "password": "Secret123!",
        "confirm_password": "Secret123!",
        "user_type": user_type_val,
        "submit": "Submit",
    }
    post_r = client.post("/signup", data=payload, follow_redirects=True)
    assert post_r.status_code == 200
    assert _user_exists(app, email)

    lower = post_r.data.lower()
    # Accept any of these success cues; adjust as needed
    assert (
        b"logout" in lower
        or b"profile" in lower
        or b"dashboard" in lower
        or b"account" in lower
    ), "Success marker not found; adjust assertion to real template."

def test_signup_email_taken(app, client):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO users (email, password, first_name, is_admin) VALUES (?,?,?,?)",
            ("exists@example.com", generate_password_hash("Whatever123!"), "Exists", 0),
        )
    r = client.post("/signup", data={
        "email": "exists@example.com",
        "password": "Whatever123!",
        "confirm_password": "Whatever123!",
        "first_name": "Exists",
        "user_type": "regular",  # adjust if different
    }, follow_redirects=True)
    assert r.status_code == 200
    html = r.data.lower()
    assert b"already" in html or b"taken" in html or b"exists" in html

def _insert_user(app, email, raw_password, first_name="Test", is_admin=0):
    pw_hash = generate_password_hash(raw_password)
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO users (email, password, first_name, is_admin) VALUES (?,?,?,?)",
            (email, pw_hash, first_name, is_admin),
        )

def test_login_success(app, client):
    _insert_user(app, "user@example.com", "CorrectPw1!")
    r = client.post("/login", data={
        "email": "user@example.com",
        "password": "CorrectPw1!",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"logged" in r.data.lower() or b"welcome" in r.data.lower()

def test_login_bad_password(app, client):
    _insert_user(app, "user2@example.com", "RightPass123!")
    r = client.post("/login", data={
        "email": "user2@example.com",
        "password": "WrongPw!",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"invalid" in r.data.lower() or b"incorrect" in r.data.lower()

def test_login_unknown_user(client):
    r = client.post("/login", data={
        "email": "nouser@example.com",
        "password": "AnyPw123!",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"not found" in r.data.lower() or b"invalid" in r.data.lower()

def test_logout(client, app):
    with client.session_transaction() as sess:
        sess["user_id"] = 999
    r = client.get("/logout", follow_redirects=True)
    assert r.status_code == 200
    with client.session_transaction() as sess:
        assert "user_id" not in sess
    assert b"logged out" in r.data.lower() or b"logout" in r.data.lower()