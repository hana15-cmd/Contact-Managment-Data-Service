import os
import sqlite3 
from flask import Flask, g 

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'teamDatabase.db')),
    SECRET_KEY='HELLO'
))

def connection_database():
    connection = sqlite3.connect(app.config['DATABASE'])
    connection.row_factory = sqlite3.Row
    return connection

def get_db(): 
    if 'db' not in g: 
        g.db = sqlite3.connect('teamDatabase.db') 
        g.db.row_factory = sqlite3.Row 
    return g.db 

def init_db(): 
    with app.app_context(): 
        db = get_db() 
        with app.open_resource('teamsData.sql', mode='r') as f: 
            db.executescript(f.read()) 
        db.commit() 

def init_database_with_dummy_data():
    with app.app_context():
        db=get_db
        with app.open_resource('schemadb.sql', mode='r') as f: 
            db.cursor().executescript(f.read())
            add_entry('Blue','London',10,'blue@db.com',4455212347)
            db.commit()



def add_entry(team_name, team_location, number_of_team_members,team_email_address,team_phone_number):
    database = get_db()
    database.execute(
        "insert into teams(TEAM_NAME,TEAM_LOCATION,NUMBER_OF_TEAM_MEMBERS,EMAIL_ADDRESS,PHONE_NUMBER)) values (?,?,?,?,?) ",
                    (team_name,team_location,number_of_team_members,team_email_address,team_phone_number))
    database.commit()


@app.cli.command('initdb') 
def initdb_command(): 
    """Initializes the database.""" 
    init_db() 
    print('Initialized the database.') 

    