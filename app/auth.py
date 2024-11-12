# import sqlite3
# from flask import Blueprint, redirect, render_template, request, flash, url_for, session, g
# from werkzeug.security import generate_password_hash, check_password_hash

# auth = Blueprint('auth', __name__)

# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#      if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
#         user = cursor.fetchone()
#         conn.close()
        
#         if user and check_password_hash(user['password'], password):
#             session['user_id'] = user['id']
#             flash("Login successful!", "success")
#             return redirect(url_for('dashboard'))  # Redirect to a dashboard or home page
#         else:
#             flash("Invalid email or password.", "error")
#             return redirect(url_for('auth.login'))
        
#      return render_template('login.html')

# @auth.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out.', category="info")
#     return redirect(url_for('auth.login'))


# @auth.route('/sign', methods=['POST', 'GET'])
# def signup():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         first_name = request.form.get('firstName')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')

#         if not all([email,first_name,password1,password2]):
#             flash ("All fields are required", "error")
#             return redirect(url_for('auth.signup'))
        
#         if password1 != password2:
#             flash("Passwords do not match.","error")
#             return redirect(url_for('auth.signup'))
        
#         if len(password1) < 8:
#             flash("Password must be at least 8 characters long.", "error")
#             return redirect(url_for('auth.signup'))
            
#         hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
        
#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()

#             cursor.execute("INSERT INTO users (email,first_name,password) VALUES (?,?, ?)",
#             (email,first_name,hashed_password))
#             conn.commit()
#             conn.close()

#             flash("Account created successfully!", "success")
#             return redirect(url_for('login'))
        
#         except sqlite3.IntegrityError:
#             flash("Username already exists.", "error")
#             return redirect(url_for('signup'))
 
#     return render_template("sign_up.html")

