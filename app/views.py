from flask import Blueprint,render_template
from flask import current_app
import os
import sqlite3
import sqlite3 as sql
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import add_entry, get_database
from flask import render_template, request, redirect, url_for, flash
import sqlite3 as sql

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

@views.route('/init_db')
def initialize_db():
    try:
        from app.models import init_db_scheme, add_dummy_teams_data
        init_db_scheme()  # Set up the database schema
        add_dummy_teams_data()  # Populate with dummy data
        flash('Database initialized successfully with dummy data!', 'success')
        return redirect(url_for('views.home'))
    except Exception as e:
        flash(f'Error during database initialization: {str(e)}', 'danger')
        return redirect(url_for('views.home'))


@views.route('/contactManager')
def contacts():
    database = get_database()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM teams")
    data = cursor.fetchall()
    if not data:
        print("No data found in the teams table.")
    else:
        for row in data:
            print(dict(row))  # Debugging output
    return render_template("index.html", datas=data)

# @views.route('/contactManager', methods=['GET', 'POST'])
# def contacts():
#     # Get search and filter query parameters from the URL (default to empty if not provided)
#     search_query = request.args.get('search', '')  # Get the search query from the URL
#     filter_column = request.args.get('filter', '')  # Get the filter column (optional)

#     # Establish database connection
#     database = get_database()
#     cursor = database.cursor()

#     # Start with the base SQL query
#     sql_query = "SELECT * FROM teams"
#     sql_params = []

#     # Modify the query based on user input
#     if search_query:
#         # If both search query and filter column are provided
#         if filter_column:
#             sql_query += f" WHERE {filter_column} LIKE ?"
#             sql_params.append(f"%{search_query}%")
#         else:
#             # If no filter column is specified, search across multiple columns
#             sql_query += """
#                 WHERE TEAM_NAME LIKE ? 
#                 OR TEAM_LOCATION LIKE ? 
#                 OR EMAIL_ADDRESS LIKE ?
#             """
#             sql_params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

#     # Execute the query with parameters (this prevents SQL injection)
#     cursor.execute(sql_query, sql_params)
#     data = cursor.fetchall()

#     # Return the template with the filtered data and search information
#     return render_template("index.html", datas=data, search_query=search_query, filter_column=filter_column)


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
            con = sql.connect(current_app.config['DATABASE'])
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

@views.route("/see_team_members/<string:id>", methods=['POST','GET'])
def see_team_members(id):
    
    # Establish database connection
    con = sql.connect(current_app.config['DATABASE'])
    try:
        cur = con.cursor()
        
        # Query to get team details
        cur.execute("SELECT * FROM teams WHERE ID=?", (id,))
        team = cur.fetchone()
        
        # If team is found, get team members (contacts)
        if team:
            cur.execute("SELECT * FROM contacts WHERE team_id=?", (id,))
            members = cur.fetchall()  # Retrieve all members associated with the team
        
            # Pass team and members information to the template
            return render_template("team_member_info.html", team=team, members=members)
        else:
            flash('Team not found', 'danger')
            return redirect(url_for("views.contacts"))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for("views.contacts"))
    finally:
        cur.close()
        con.close()


@views.route("/edit_team/<string:id>",methods=['POST','GET'])
def edit_team(id):
    if request.method=='POST':
        team_name=request.form['teamName']
        team_location=request.form['teamLocation']
        number_of_team_members=request.form['numberOfTeamMembers']
        team_email_address=request.form['EmailAddress']
        team_phone_number=request.form['PhoneNumber']
        con = sql.connect(current_app.config['DATABASE'])
        cur=con.cursor()
        cur.execute("""
            UPDATE teams 
            SET TEAM_NAME=?, TEAM_LOCATION=?, NUMBER_OF_TEAM_MEMBERS=?, EMAIL_ADDRESS=?, PHONE_NUMBER=? 
            WHERE id=?
        """, (team_name, team_location, number_of_team_members, team_email_address, team_phone_number, id))
        con.commit()
        flash('Team Updated','success')
        return redirect(url_for("views.contacts"))
    con = sql.connect(current_app.config['DATABASE'])
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("SELECT * FROM teams where ID=?",(id,))
    data=cur.fetchone()
    return render_template('edit_team.html',datas=data)

@views.route("/delete_team/<string:id>", methods=['GET'])
def delete_teams(id):
    con = sql.connect(current_app.config['DATABASE'])
    cur = con.cursor()
    cur.execute("DELETE FROM teams WHERE ID=?", (id,))  # Add a comma here to make it a tuple
    con.commit()
    con.close()  
    flash('Team Deleted', 'warning')
    return redirect(url_for("views.contacts"))

@views.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You were successfully logged out')
    return redirect(url_for('views.login'))
