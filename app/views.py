from flask import Blueprint,render_template

import os
import sqlite3
import sqlite3 as sql
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'database.db')),
    SECRET_KEY=['hihihi']))


def connection_database():
    connection = sqlite3.connect(app.config['DATABASE'])
    connection.row_factory = sqlite3.Row
    return connection

def get_database():
    if not hasattr(g, 'sqlite_database'):
        g.sqlite_database = connection_database()
    return g.sqlite_database

def init_db_scheme():
    with app.app_context():
        database = get_database()
        with app.open_resource('schemadb.sql', mode='r') as f:
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

views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template("homepage.html")

@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not all([email, first_name, password, confirm_password]):
            flash('All fields are required.', category='error')
            return redirect(url_for('views.signup'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.',category='error')
            return redirect(url_for('views.signup'))

        database = get_database()
        existing_user = database.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing_user:
            flash('User already exists. Please log in.', category='error')
            return redirect(url_for('views.login'))

        add_entry(email, first_name, password)
        flash('Registration successful! Please log in.', category='success')
        return redirect(url_for('views.login'))
    return render_template('sign.html')

@views.route('/login/',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        database = get_database()
        user = database.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['first_name']
            flash('You were successfully logged in')
            return redirect(url_for('views.contacts'))  # Redirect to home after login
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@views.route('/contactManager')
def contacts():
    database = get_database()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM teams")
    data = cursor.fetchall()
    return render_template("index.html", datas=data)

from flask import render_template, request, redirect, url_for, flash
import sqlite3 as sql

@views.route("/add_team", methods=['POST', 'GET'])
def add_team():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        team_location = request.form.get('team_location')
        number_of_team_members = request.form.get('number_of_team_members')
        team_email_address = request.form.get('team_email_address')
        team_phone_number = request.form.get('team_phone_number')

        if not all([team_name, team_location, number_of_team_members, team_email_address, team_phone_number]):
            flash('All fields are required!', category='error')
            return redirect(url_for('views.add_team'))

        try:
            number_of_team_members = int(number_of_team_members)
        except ValueError:
            flash('Invalid input for number of team members!', category='error')
            return redirect(url_for('views.add_team'))

        if not team_phone_number.isdigit():
            flash('Invalid phone number! Please ensure it contains only digits.', category='error')
            return redirect(url_for('views.add_team'))
        try:
            con = sql.connect(app.config['DATABASE'])
            cur = con.cursor()

            # Insert data into the database
            cur.execute(
                """
                INSERT INTO teams (TEAM_NAME, TEAM_LOCATION, NUMBER_OF_TEAM_MEMBERS, EMAIL_ADDRESS, PHONE_NUMBER)
                VALUES (?, ?, ?, ?, ?)
                """,
                (team_name, team_location, number_of_team_members, team_email_address, team_phone_number)
            )
            con.commit()
            cur.execute("SELECT * FROM teams")
            print("Database contents:", cur.fetchall())

            flash('Team added successfully!', category='success')
        except Exception as e:
            flash(f'Error occurred while adding the team: {str(e)}', category='error')
        finally:
            con.close()

        return redirect(url_for("views.contacts"))

    return render_template('add_team.html')

@views.route("/edit_team/<string:uid>",methods=['POST','GET'])
def edit_team(id):
    if request.method=='POST':
        team_name=request.form['teamName']
        team_location=request.form['teamLocation']
        number_of_team_members=request.form['numberOfTeamMembers']
        team_email_address=request.form['EmailAddress']
        team_phone_number=request.form['PhoneNumber']
        con=sql.connect("teamDatabase.db")
        cur=con.cursor()
        cur.execute("update teams set TEAM_NAME=?,CONTACT=? where ID=?",(team_name,team_location,number_of_team_members,team_email_address,team_phone_number,id))
        con.commit()
        flash('Team Updated','success')
        return redirect(url_for("index"))
    con=sql.connect("teamDatabase.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from teams where ID=?",(id,))
    data=cur.fetchone()
    return render_template("edit_team.html",datas=data)
    
@views.route("/delete_team/<string:uid>",methods=['GET'])
def delete_teams(id):
    con=sql.connect("teamDatabase.db")
    cur=con.cursor()
    cur.execute("delete from teams where ID=?",(id))
    con.commit()
    flash('Team Deleted','warning')
    return redirect(url_for("index"))

@views.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You were successfully logged out')
    return redirect(url_for('views.login'))