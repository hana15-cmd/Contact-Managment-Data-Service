import sqlite3
from werkzeug.security import generate_password_hash
from unittest import mock

DEFAULT_PASSWORD = "Pass123!"

def create_test_user_in_db(app, email="editor@example.com", first_name="Editor", is_admin=1):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO users (email, password, first_name, is_admin) VALUES (?,?,?,?)",
            (email, generate_password_hash(DEFAULT_PASSWORD), first_name, is_admin),
        )
        user_id = con.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()[0]
    return user_id, email

def force_login(client, user_id, is_admin=False):
    # Prime session backend so open_session returns a session
    client.get("/")
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    # Ensure Flask-Login resolves to an authenticated user
    return mock.patch(
        "app.user_auth.User.get_by_id",
        return_value=type("U", (), {
            "id": int(user_id),
            "is_authenticated": True,
            "is_active": True,
            "is_anonymous": False,
            "is_admin": is_admin,
            "get_id": lambda self: str(user_id),
        })()
    )

def create_team(app, name, members=1):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO teams (team_name, team_location, number_of_team_members, email_address) VALUES (?,?,?,?)",
            (name, "Remote", members, f"{name.lower()}@example.com"),
        )
        team_id = con.execute("SELECT id FROM teams WHERE team_name=?", (name,)).fetchone()[0]
    return team_id

def create_contact(app, employee_name, email_address, phone_number, team_id):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO contacts (employee_name, email_address, phone_number, team_id) VALUES (?,?,?,?)",
            (employee_name, email_address, phone_number, team_id),
        )
        contact_id = con.execute("SELECT id FROM contacts WHERE employee_name=?", (employee_name,)).fetchone()[0]
    return contact_id

def get_contact(app, contact_id):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.row_factory = sqlite3.Row
        return con.execute("SELECT * FROM contacts WHERE id=?", (contact_id,)).fetchone()

def test_edit_member_requires_login(app, client):
    t = create_team(app, "Alpha")
    c = create_contact(app, "John", "john@example.com", "1111111111", t)
    r = client.get(f"/edit_team_member/{c}")
    assert r.status_code == 302
    # Accept different unauthorized targets
    assert ("/login" in r.headers.get("Location", "")) or (r.headers.get("Location", "") == "/")

def test_edit_member_not_found(app, client):
    uid, _ = create_test_user_in_db(app)
    patcher = force_login(client, uid)
    patcher.start()
    r = client.get("/edit_team_member/99999", follow_redirects=True)
    patcher.stop()
    assert r.status_code == 200  # redirected target renders
    assert b"edit team member" not in r.data or b"not found" in r.data.lower()

def test_edit_member_invalid_keeps_original(app, client):
    uid, _ = create_test_user_in_db(app)
    patcher = force_login(client, uid)
    patcher.start()
    t = create_team(app, "Alpha")
    c = create_contact(app, "Dave", "dave@example.com", "6666666666", t)
    payload = {
        "employee_name": "",          # invalid
        "email_address": "bad-email", # invalid
        "phone_number": "7777777777",
        "team_id": str(t),
        "submit": "Submit",
    }
    r = client.post(f"/edit_team_member/{c}", data=payload, follow_redirects=True)
    patcher.stop()
    assert r.status_code == 200
    row = get_contact(app, c)
    assert row["employee_name"] == "Dave"
    assert b"required" in r.data.lower() or b"invalid" in r.data.lower() or b"error" in r.data.lower()