from flask import Flask,request,session,g,redirect, url_for,render_template,flash
import sqlite3,os

app = Flask (__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'data.db')),
    SECRET_KEY=os.getenv('SECRET_KEY', 'development key'),
    USERNAME=os.getenv('USERNAME', 'admin'),
    PASSWORD=os.getenv('PASSWORD', 'default')
))

def connect_database():
    connection = sqlite3.connect(app.config['DATABASE'])
    connection.row_factory = sqlite3.Row 
    return connection 

def initalise_database_schema():
    with app.app_context():
        database = get_database()
        with app.open_resource('schema.sql', mode = 'r') as f:
            database.executescript(f.read())
            database.commit()

def get_database():
    if not hasattr (g, 'sqlite_database'):
        g.sqlite_database = connect_database()
        return g.sqlite_database 
    
@app.teardown_appcontext
def close_database(error):
    if hasattr(g,'sqlite_database'):
        g.sqlite_database.close()

@app.route('/')
def show_teams():
    database = get_database()
    cursor = database.execute('select team_name, team_location, Number_of_members from teams order by id desc')
    teams = cursor.fetchall()
    return render_template('index.html', teams=teams)

if __name__ == '__main__':
    initalise_database_schema()
    app.run()