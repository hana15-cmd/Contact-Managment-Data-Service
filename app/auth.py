
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import SignupForm, is_email_taken
from app.models import add_entry, get_database


auth = Blueprint('auth',__name__)


@auth.route('/login/', methods=['GET', 'POST'])
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
            session['is_admin'] = user['is_admin']  # Store admin status in session
            flash('You were successfully logged in')
            return redirect(url_for('views.contacts'))  # Redirect to home after login
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()  # Assuming you have a Flask-WTF form defined for signup
    if form.validate_on_submit():
        # Extract data from the form
        email = form.email.data
        first_name = form.first_name.data
        password = form.password.data
        user_type = form.user_type.data

        # Check if email already exists in the database
        if is_email_taken(email):
            flash('User already exists. Please log in.', category='error')
            return redirect(url_for('auth.login'))

        # Add entry to the database
        is_admin = (user_type == 'admin')
        add_entry(email, first_name, password, is_admin)

        flash('Registration successful! Please log in.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)


# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         # Get form data
#         email = request.form['email']
#         first_name = request.form['first_name']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']
#         user_type = request.form.get('user_type')  # Either 'admin' or 'regular'

#         # Validate the form
#         if not all([email, first_name, password, confirm_password]):
#             flash('All fields are required.', category='error')
#             return redirect(url_for('auth.signup'))

#         if password != confirm_password:
#             flash('Passwords do not match. Please try again.', category='error')
#             return redirect(url_for('auth.signup'))

#         # Check if email already exists in the database
#         database = get_database()  # Assuming you have a function to connect to your DB
#         existing_user = database.execute(
#             "SELECT * FROM users WHERE email = ?", (email,)
#         ).fetchone()

#         if existing_user:
#             flash('User already exists. Please log in.', category='error')
#             return redirect(url_for('auth.login'))

#         # Add entry to the database
#         is_admin = user_type == 'admin'  # Set admin based on user selection
#         add_entry(email, first_name, password, is_admin)  # Assuming add_entry handles the database insert

#         flash('Registration successful! Please log in.', category='success')
#         return redirect(url_for('auth.login'))

#     return render_template('signup.html')  # Assuming your HTML file is named 'signup.html'



# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         first_name = request.form['first_name']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']

#         if not all([email, first_name, password, confirm_password]):
#             flash('All fields are required.', category='error')
#             return redirect(url_for('auth.signup'))

#         if password != confirm_password:
#             flash('Passwords do not match. Please try again.',category='error')
#             return redirect(url_for('auth.signup'))

#         database = get_database()
#         existing_user = database.execute(
#             "SELECT * FROM users WHERE email = ?", (email,)
#         ).fetchone()

#         if existing_user:
#             flash('User already exists. Please log in.', category='error')
#             return redirect(url_for('auth.login'))

#         add_entry(email, first_name, password)
#         flash('Registration successful! Please log in.', category='success')
#         return redirect(url_for('auth.login'))
#     return render_template('sign.html')

# @auth.route('/login/',methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         database = get_database()
#         user = database.execute(
#             "SELECT * FROM users WHERE email = ?", (email,)
#         ).fetchone()

#         if user and check_password_hash(user['password'], password):
#             session['user_id'] = user['id']
#             session['user_name'] = user['first_name']
#             flash('You were successfully logged in')
#             return redirect(url_for('views.contacts'))  # Redirect to home after login
#         else:
#             flash('Invalid username or password')

#     return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You were successfully logged out')
    return redirect(url_for('auth.login'))



