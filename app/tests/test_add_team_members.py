import sqlite3
from werkzeug.security import generate_password_hash

PASSWORD = "Pass123!"

def _insert_user(app, email="tester@example.com", first_name="Tester", is_admin=1):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO users (email, password, first_name, is_admin) VALUES (?,?,?,?)",
            (email, generate_password_hash(PASSWORD), first_name, is_admin),
        )
        user_id = con.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()[0]
    return user_id, email

def _force_login(client, user_id):
    # Fallback direct session (avoids form login issues)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True

def _insert_team(app, name="Alpha", members=1):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        con.execute(
            "INSERT INTO teams (team_name, team_location, number_of_team_members, email_address) VALUES (?,?,?,?)",
            (name, "Remote", members, f"{name.lower()}@example.com"),
        )
        team_id = con.execute("SELECT id FROM teams WHERE team_name=?", (name,)).fetchone()[0]
    return team_id

def _contact_exists(app, employee_name):
    with sqlite3.connect(app.config["DATABASE"]) as con:
        return con.execute(
            "SELECT 1 FROM contacts WHERE employee_name=?", (employee_name,)
        ).fetchone() is not None

def test_add_team_member_requires_login(app, client):
    team_id = _insert_team(app)
    r = client.get(f"/add_team_member/{team_id}")
    assert r.status_code == 302
    assert "/login" in r.headers.get("Location", "")

def test_add_team_member_get_renders_form(app, client):
    user_id, _ = _insert_user(app)
    _force_login(client, user_id)
    team_id = _insert_team(app)
    r = client.get(f"/add_team_member/{team_id}")
    assert r.status_code == 200
    assert b"Add" in r.data or b"Member" in r.data

def test_add_team_member_post_invalid(app, client):
    user_id, _ = _insert_user(app)
    _force_login(client, user_id)
    team_id = _insert_team(app)
    payload = {
        "employee_name": "",  # Invalid: required field
        "email_address": "invalid-email",  # Invalid email format
        "phone_number": "1234567890",
        "team_id": str(team_id),
        "submit": "Submit",
    }
    r = client.post(f"/add_team_member/{team_id}", data=payload, follow_redirects=True)
    assert r.status_code == 200  # Form re-rendered due to validation errors
    assert b"This field is required" in r.data or b"Invalid email address" in r.data