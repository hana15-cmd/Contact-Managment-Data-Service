import sqlite3
from flask import Blueprint, redirect, render_template,request,flash, url_for

from app.flaskloginin import load_user, verify_user

auth = Blueprint('auth',__name__)

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            flash('Logged in successfully!')
            return redirect(url_for('views.home'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

   
@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/sign', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Perform validation checks within the POST request scope
        if len(email) < 2:
            flash('Email length must be more than 2 characters', category="error")
            print("email"),
        elif len(firstName) < 1: 
            flash('First Name length must be more than 1 character', category="error")
        elif password1 != password2:
            flash('Passwords do not match', category="error")
        elif len(password1) < 8:
            flash('Password must have more than 8 characters', category="error")
        else:
            flash('Successfully created account!', category="success") 
    return render_template("sign_up.html")

