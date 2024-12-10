import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, flash, g, redirect, session, url_for
from functools import wraps

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
        add_dummy_contacts_data()
        database.commit()

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
        return redirect(url_for('auth.login'))  # Assuming you want to redirect to login
    
    except sqlite3.IntegrityError as e:
        # Handle specific IntegrityError if any
        flash("An error occurred while creating the user.", "danger")
        return redirect(url_for('auth.signup'))

def add_dummy_teams_data():
    database = get_database()
    try:
        print("Clearing and adding dummy data to the teams table...")
        database.execute("DELETE FROM teams")  # Clear existing data
        database.execute("""
            INSERT INTO teams (team_name, team_location, number_of_team_members, email_address, phone_number)
            VALUES
            ('Rover', 'Pune', 7, 'rover@teams.com', '+917585858585'),  
            ('Grogu', 'London', 10, 'grogu@teams.com', '+447234567890'),  
            ('Galaxy', 'Rome', 10, 'galaxy@teams.com', '+393975421256'),  
            ('Stars', 'Barcelona', 8, 'stars@teams.com', '+34633333333'), 
            ('Moon', 'London', 7, 'moon@teams.com', '+447675757444'),  
            ('Saturn', 'Bangalore', 10, 'saturn@teams.com', '+915555555555'), 
            ('Midnight', 'Pune', 8, 'midnight@teams.com', '+917666688688'),  
            ('Twilight', 'Manchester', 8, 'twilight@teams.com', '+447999787564'), 
            ('Yoda', 'Barcelona', 8, 'yoda@teams.com', '+34785832244'), 
            ('Gravity', 'Bangalore', 10, 'gravity@teams.com', '+915555421445'),  
            ('Solar', 'Pune', 8, 'solar@teams.com', '+917442424242'),
            ('Infinity', 'Manchester', 8, 'infinity@teams.com', '+447746274282'),
            ('Beyond', 'London', 8, 'beyond@teams.com', '+4455678906');
        """)
        database.commit()
        print("Dummy data successfully added to teams!")
    except sqlite3.Error as e:
        print(f"Error adding dummy teams data: {e}")

def add_dummy_contacts_data():
    database = get_database()
    try:
        print("Clearing and adding dummy data to the contacts table...")
        database.execute("DELETE FROM contacts")  # Clear existing data

        # Insert dummy data with correct team_id values
        database.execute("""
            INSERT INTO contacts (EMPLOYEE_NAME, EMAIL_ADDRESS, PHONE_NUMBER, TEAM_ID)
            VALUES
                ('John Doe', 'john.doe@teams.com', '1234567890', 37),
                ('Jane Smith', 'jane.smith@teams.com', '9876543210', 296),
                ('Lucy Brown', 'lucy.brown@teams.com', '5555555555', 269); -- Assuming 140 is another valid team ID
        """)
        database.commit()
        print("Dummy data successfully added to contacts!")
    except sqlite3.Error as e:
        print(f"Error adding dummy contacts data: {e}")
    

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin privileges required.', 'danger')
            return redirect(url_for("views.contacts"))
        return f(*args, **kwargs)
    return decorated_function
