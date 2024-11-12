# from flask import render_template, request, redirect, url_for, flash
# from app import app
# from app.database import get_database, add_entry

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         first_name = request.form['first_name']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']

#         if not all([email, first_name, password, confirm_password]):
#             flash('All fields are required.', 'error')
#             return redirect(url_for('signup'))

#         if password != confirm_password:
#             flash('Passwords do not match. Please try again.','error')
#             return redirect(url_for('signup'))

#         database = get_database()
#         existing_user = database.execute(
#             "SELECT * FROM users WHERE email = ?", (email,)
#         ).fetchone()

#         if existing_user:
#             flash('User already exists. Please log in.', 'error')
#             return redirect(url_for('login'))

#         add_entry(email, first_name, password)
#         flash('Registration successful! Please log in.', 'success')
#         return redirect(url_for('login'))
        
#     return render_template('sign_up.html')