import random
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, flash, g, redirect, session, url_for
from functools import wraps

# Create a connection to the database
def connection_database():
    connection = sqlite3.connect(current_app.config['DATABASE'])
    connection.row_factory = sqlite3.Row  # Allows access by column name
    return connection


# Get or create the database connection attached to the Flask global context (g)
def get_database():
    if not hasattr(g, 'sqlite_database'):
        g.sqlite_database = connection_database()
    return g.sqlite_database


# Initialize the database schema (tables, etc.), and add dummy data
def init_db_scheme():
    with current_app.app_context():
        database = get_database()
        with current_app.open_resource('database_logic/schemadb.sql', mode='r') as f:
            database.executescript(f.read())
        add_dummy_teams_data()  # Adding dummy teams
        add_dummy_contacts_data()  # Adding dummy contacts
        database.commit()


# Add a new user to the users table with email and password
def add_entry(email, first_name, password, is_admin=False):
    # Check if the email already exists
    database = get_database()
    existing_user = database.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()

    if existing_user:
        flash("Email is already taken, please use a different one.", "danger")
        return redirect(url_for('auth.signup'))  # Assuming you have a signup route

    # If email is not found, proceed with inserting the new user
    hashed_password = generate_password_hash(password)
    try:
        database.execute(
            """
            INSERT INTO users (email, first_name, password, is_admin)
            VALUES (?, ?, ?, ?)
            """,
            (email, first_name, hashed_password, is_admin)
        )
        database.commit()
        flash("User created successfully!", "success")
        return redirect(url_for('auth.login'))  # Redirect to login after successful signup
    
    except sqlite3.IntegrityError as e:
        # Handle specific IntegrityError if any
        flash("An error occurred while creating the user.", "danger")
        return redirect(url_for('auth.signup'))


# Add dummy teams data to the teams table
def add_dummy_teams_data():
    database = get_database()
    try:
        print("Clearing and adding dummy data to the teams table...")
        database.execute("DELETE FROM teams")  # Clear existing data
        database.execute("""
            INSERT INTO teams (team_name, team_location, number_of_team_members, email_address)
            VALUES
                ('Rover', 'Pune', 7, 'rover@teams.com'),
                ('Grogu', 'London', 10, 'grogu@teams.com'),
                ('Galaxy', 'Rome', 10, 'galaxy@teams.com'),
                ('Stars', 'Barcelona', 8, 'stars@teams.com'),
                ('Moon', 'London', 7, 'moon@teams.com'),
                ('Saturn', 'Bangalore', 10, 'saturn@teams.com'),
                ('Midnight', 'Pune', 8, 'midnight@teams.com'),
                ('Twilight', 'Manchester', 8, 'twilight@teams.com'),
                ('Yoda', 'Barcelona', 8, 'yoda@teams.com'),
                ('Gravity', 'Bangalore', 10, 'gravity@teams.com'),
                ('Solar', 'Pune', 8, 'solar@teams.com'),
                ('Infinity', 'Manchester', 8, 'infinity@teams.com'),
                ('Beyond', 'London', 8, 'beyond@teams.com');
        """)
        database.commit()
        print("Dummy data successfully added to teams!")
    except sqlite3.Error as e:
        print(f"Error adding dummy teams data: {e}")


# Add dummy contacts data to the contacts table, ensuring each team has at least 3 dummy contacts
def add_dummy_contacts_data():
    database = get_database()
    try:
        print("Clearing and adding dummy data to the contacts table...")

        # Clear existing data
        database.execute("DELETE FROM contacts")
        database.commit()

        # Fetch available team IDs
        cursor = database.cursor()
        cursor.execute("SELECT ID FROM teams")
        team_ids = [row[0] for row in cursor.fetchall()]

        if not team_ids:
            print("No teams found in the database. Add teams before adding dummy contacts.")
            return

        # Prepare a list of dummy contact data
        dummy_data = [
            ('John Doe', 'john.doe@teams.com', '+1234567890'),
            ('Jane Smith', 'jane.smith@teams.com', '+9876543210'),
            ('Lucy Brown', 'lucy.brown@teams.com', '+5555555555'),
            ('Alice Green', 'alice.green@teams.com', '+6789012345'),
            ('Michael Blue', 'michael.blue@teams.com', '+55987654321'),
            ('Davide Black', 'david.black@teams.com', '+2345678901'),
            ('Emily White', 'emily.white@teams.com', '+3456789012'),
            ('Daniel Yellow', 'daniel.yellow@teams.com', '+4567890123'),
            ('Phillip Skylar', 'sophie.red@teams.com', '+5678901234'),
            ('Eliza Renoylds', 'tom.green@teams.com', '+6789012345')
        ]

        # Ensure each team gets at least 3 contacts
        for team_id in team_ids:
            for i in range(3):  # Add 3 contacts per team
                contact = random.choice(dummy_data)  # Choose a random contact from the dummy data
                database.execute("""
                    INSERT INTO contacts (EMPLOYEE_NAME, EMAIL_ADDRESS, PHONE_NUMBER, TEAM_ID)
                    VALUES (?, ?, ?, ?)
                """, (contact[0], contact[1], contact[2], team_id))

        database.commit()
        print("Dummy data successfully added to contacts!")

    except sqlite3.Error as e:
        print(f"Error adding dummy contacts data: {e}")


# Ensure only admins can access certain views
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin privileges required.', 'danger')
            return redirect(url_for("views.contacts"))
        return f(*args, **kwargs)
    return decorated_function
