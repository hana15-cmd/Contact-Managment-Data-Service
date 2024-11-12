from flask import Blueprint,render_template
import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'database.db')),
    SECRET_KEY=os.urandom(24),  # Use a random secret key for development
))

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
            database.commit()

def add_entry(email, first_name, password):
    database = get_database()
    hashed_password = generate_password_hash(password)
    database.execute(
        "INSERT INTO users (email, first_name, password) VALUES (?, ?, ?)",
        (email, first_name, hashed_password)
    )
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
            flash('All fields are required.', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.','error')
            return redirect(url_for('signup'))

        database = get_database()
        existing_user = database.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing_user:
            flash('User already exists. Please log in.', 'error')
            return redirect(url_for('login'))

        add_entry(email, first_name, password)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
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
def conatcts():
    return render_template('tables.html')

@views.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You were successfully logged out')
    return redirect(url_for('login'))