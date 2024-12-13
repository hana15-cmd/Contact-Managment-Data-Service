from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import SignupForm, is_email_taken
from app.database_logic.models import add_entry, get_database
from app.user_auth import User

auth = Blueprint('auth', __name__)

@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Get the user from the database using email
        user = User.get_by_email(email)

        if user and check_password_hash(user.password, password):
            # Log the user in using Flask-Login
            login_user(user)

            # Store additional info in the session if needed
            session['user_id'] = user.id
            session['user_name'] = user.first_name  # Store the user's first name
            session['is_admin'] = user.is_admin  # Store admin status in session

            flash('You were successfully logged in', category='success')
            return redirect(url_for('views.contacts'))  # Redirect to contacts or dashboard after login

        else:
            flash('Invalid username or password', category='error')

    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()  # Assuming you have a Flask-WTF form defined for signup
    if form.validate_on_submit():
        # Extract data from the form
        email = form.email.data
        first_name = form.first_name.data
        password = form.password.data
        user_type = form.user_type.data

        # Add entry to the database, will handle email uniqueness check
        is_admin = (user_type == 'admin')
        result = add_entry(email, first_name, password, is_admin)

        if result:
            flash('Registration successful! Please log in.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('User already exists. Please log in.', category='error')
            return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)


@auth.route('/logout', methods=['GET'])
def logout():
    # Clear session variables upon logout
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('is_admin', None)  # Remove admin info from session
    
    flash('You were successfully logged out', category='success')
    return redirect(url_for('auth.login'))
