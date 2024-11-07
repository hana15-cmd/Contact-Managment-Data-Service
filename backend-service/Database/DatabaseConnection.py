# from flask import Flask, request, session, g, redirect, url_for, render_template, flash, views
# import sqlite3
# import os

# app = Flask(__name__)

# # Configuration settings
# app.config.update(dict(
#     DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'data.db')),
#     SECRET_KEY=os.getenv('SECRET_KEY', 'development key'),
#     USERNAME=os.getenv('USERNAME', 'admin'),
#     PASSWORD=os.getenv('PASSWORD', 'default')
# ))

# # Function to connect to the database
# def connect_database():
#     connection = sqlite3.connect(app.config['DATABASE'])
#     connection.row_factory = sqlite3.Row
#     return connection

# # Function to initialise the database schema
# def initialise_database_schema():
#     try:
#         with app.app_context():
#             database = get_database()
#             with app.open_resource('schema.sql', mode='r') as f:
#                 sql_script = f.read()
#                 print("SQL script to execute:", sql_script)  # Debugging line
#                 database.executescript(sql_script)
#                 database.commit()
#                 print("Database schema initialised successfully.")
#     except Exception as e:
#         print("Error intialising database schema:", e)
 
# # Function to get the database connection
# def get_database():
#     if not hasattr(g, 'sqlite_database'):
#         g.sqlite_database = connect_database()
#     return g.sqlite_database

# # Initializes the database with schema and a dummy entry
# def init_database_with_dummy_data():
#     with app.app_context():
#         database = get_database()
#         with app.open_resource('schema.sql', mode='r') as f:
#             database.cursor().executescript(f.read())
#             add_entry('Trapeze', 'London', 10)
#             add_entry('Aqua',' Pune', 8)
#             database.commit()

# def add_entry(team_name, team_location, number_of_members):
#     database = get_database()
#     database.execute(
#         'INSERT INTO teams (team_name, team_location, Number_of_members) VALUES ( ?, ?, ?)',
#         (team_name, team_location, number_of_members)
#     )
#     database.commit()

# # Close the database connection after the request is finished
# @app.teardown_appcontext
# def close_database(error):
#     if hasattr(g, 'sqlite_database'):
#         g.sqlite_database.close()

# @app.route('/')
# def show_teams():
#     database = get_database()
#     try:
#         cursor = database.execute('SELECT team_name, team_location, Number_of_members FROM teams ORDER BY id DESC')
#         teams = cursor.fetchall()
#         print("Fetched teams:", teams)  # Debugging line
#         return render_template('index.html', teams=teams)
#     except Exception as e:
#         print("Error fetching teams:", e)  # This will print the error if there's a database issue
#         return "An error occurred while fetching teams.", 500
    
# @views.route('/hs')
# def homePage():
#     return "<h1>Testing testing !</h1>"
    
# # Main block to run the app
# if __name__ == '__main__':
#     init_database_with_dummy_data()
#     app.run(debug=True, host='0.0.0.0', port=5001)
