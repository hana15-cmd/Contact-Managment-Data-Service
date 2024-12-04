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
        add_dummy_contacts_data()
        database.commit()

    
def add_entry(email, first_name, password):
    database = get_database()
    hashed_password = generate_password_hash(password)
    database.execute(
        "INSERT INTO users (email, first_name, password) VALUES (?, ?, ?)",
        (email, first_name, hashed_password)
    )
    database.commit()


def add_dummy_teams_data():
    database = get_database()
    try:
        print("Clearing and adding dummy data to the teams table...")
        database.execute("DELETE FROM teams")  # Clear existing data
        database.execute("""
            INSERT INTO teams (team_name, team_location, number_of_team_members, email_address, phone_number)
            VALUES
                ('Rover', 'Pune', 7, 'rover@teams.com', '57585858'),
                ('Grogu', 'London', 10, 'grogu@teams.com', '2345678902'),
                ('Galaxy', 'Rome', 10, 'galaxy@teams.com', '9754212567'),
                ('Stars', 'Barcelona', 8, 'stars@teams.com', '33333333'),
                ('Moon', 'London', 7, 'moon@teams.com', '67575744'),
                ('Saturn', 'Bangalore', 10, 'saturn@teams.com', '5555555'),
                ('Midnight', 'Pune', 8, 'midnight@teams.com', '666688688'),
                ('Twilight', 'Manchester', 8, 'twilight@teams.com', '999787564'),
                ('Yoda', 'Tokyo', 8, 'yoda@teams.com', '4444444446'),
                ('Gravity', 'Bangalore', 10, 'gravity@teams.com', '555555421445'),
                ('Solar', 'Pune', 8, 'solar@teams.com', '44242424'),
                ('Infinity', 'Manchester', 8, 'infinity@teams.com', '74627428'),
                ('Beyond', 'Tokyo', 8, 'beyond@teams.com', '1111333312');
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
            INSERT INTO contacts (NAME, EMAIL_ADDRESS, PHONE_NUMBER, TEAM_ID)
            VALUES
                ('John Doe', 'john.doe@teams.com', '1234567890', 37),
                ('Jane Smith', 'jane.smith@teams.com', '9876543210', 296),
                ('Lucy Brown', 'lucy.brown@teams.com', '5555555555', 269); -- Assuming 140 is another valid team ID
        """)
        database.commit()
        print("Dummy data successfully added to contacts!")
    except sqlite3.Error as e:
        print(f"Error adding dummy contacts data: {e}")
