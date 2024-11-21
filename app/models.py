import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, g


def connection_database():
    connection = sqlite3.connect(current_app.config['DATABASE'])
    connection.row_factory = sqlite3.Row
    return connection

def get_database():
    if not hasattr(g, 'sqlite_database'):
        g.sqlite_database = connection_database()
    return g.sqlite_database

def init_db_scheme():
    with current_app.app_context():
        database = get_database()
        with current_app.open_resource('schemadb.sql', mode='r') as f:
            database.executescript(f.read())
        add_dummy_teams_data()
        database.commit()

def add_entry(email, first_name, password):
    database = get_database()
    hashed_password = generate_password_hash(password)
    database.execute(
        "INSERT INTO users (email, first_name, password) VALUES (?, ?, ?)",
        (email, first_name, hashed_password)
    )
    database.commit()

# def add_dummy_teams_data():
#     database = get_database()
    # database.execute("""
    #     INSERT INTO teams (team_name, team_location, number_of_team_members, email_address, phone_number)
    #     VALUES
    #         ('Rover', 'Pune', 7, 'rover@teams.com', 1234567890),
    #         ('Grogu', 'London', 10, 'grogu@teams.com', 2345678901),
    #         ('Yoda', 'Tokyo', 8, 'yoda@teams.com', 3456789012);
    # """)
    # database.commit()

def add_dummy_teams_data():
    database = get_database()
    database.execute("DELETE FROM teams")  # Clears the table
    database.execute("""
        INSERT INTO teams (team_name, team_location, number_of_team_members, email_address, phone_number)
        VALUES
            ('Rover', 'Pune', 7, 'rover@teams.com', 1234567890),
            ('Grogu', 'London', 10, 'grogu@teams.com', 2345678901),
            ('Yoda', 'Tokyo', 8, 'yoda@teams.com', 3456789012);
    """)
    database.commit()
