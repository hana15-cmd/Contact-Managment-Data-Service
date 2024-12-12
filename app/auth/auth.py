
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_user
from werkzeug.security import check_password_hash
from app.forms import SignupForm
from app.database_logic.models import add_entry
from app.user_auth import User

auth = Blueprint('auth', __name__)


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.get_by_email(email)

        if user and check_password_hash(user.password, password):
            # Log the user in using Flask-Login
            login_user(user)

            flash('You were successfully logged in', category='success')
            return redirect(url_for('views.contacts'))  # Redirect to contacts or dashboard after login

        else:
            flash('Invalid username or password', category='error')
            return redirect(url_for('auth.login'))  # Return a 302 redirect to the login page

    return render_template('auth/login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Extract data from the form
        email = form.email.data
        first_name = form.first_name.data
        password = form.password.data
        user_type = form.user_type.data

        is_admin = (user_type == 'admin')
        result = add_entry(email, first_name, password, is_admin)

        if result:
            flash('Registration successful! Please log in.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('User already exists. Please log in.', category='error')
            return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You were successfully logged out, ')
    return redirect(url_for('auth.login'))

