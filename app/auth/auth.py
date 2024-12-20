from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import SignupForm, is_email_taken
from app.database_logic.models import add_entry, get_database
from app.user_auth import User

auth = Blueprint( 'auth', __name__ )


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm() 

    if form.validate_on_submit():
        # Extract data from the form
        email = form.email.data
        first_name = form.first_name.data
        password = form.password.data
        user_type = form.user_type.data

        # Determine if the user is an admin
        is_admin = (user_type == 'admin')

        # Attempt to add the user
        result = add_entry(email, first_name, password, is_admin)

        if result == 'success':
            flash('Registration successful! Please log in.', category='success')
            return redirect(url_for('auth.login'))

        elif isinstance(result, tuple) and result[0] == 'email_taken':
            # Display the name of the user associated with the email
            flash(
                f"Email is already taken by user. Please use a different one.",
                category='danger'
            )

        else:  # For 'error' or any other unexpected result
            flash('An unexpected error occurred. Please try again.', category='danger')

    # Render the signup form if validation failed or an error occurred
    return render_template('auth/signup.html', form=form)



@auth.route( '/login/', methods=['GET', 'POST'] )
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Get the user from the database using email
        user = User.get_by_email( email )

        if user and check_password_hash( user.password, password ):
            # Log the user in using Flask-Login
            login_user( user )

            # Store additional info in the session if needed
            session['user_id'] = user.id
            session['user_name'] = user.first_name  # Store the user's first name
            session['is_admin'] = user.is_admin  # Store admin status in session

            flash( 'You were successfully logged in', category='success' )
            return redirect( url_for( 'views.contacts' ) )  
        else:
            flash( 'Invalid username or password', category='error' )

    return render_template( 'auth/login.html' )


@auth.route('/logout', methods=['GET'])
def logout():
    # Log the user out using Flask-Login
    logout_user()
    
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('is_admin', None)

    flash('You were successfully logged out', category='success')
    return redirect(url_for('auth.login'))
