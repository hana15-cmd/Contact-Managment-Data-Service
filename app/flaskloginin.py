from flask import Flask,g
import sqlite3
from flask_login import LoginManger, UserMixin

login_manager = LoginManger()
login_manager.login_view ='login'

DATABASE = 'login.db'

def create_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(''' CREATE TABLE IF NOT EXISTS login(
                    user_id INTERGER PRIMARY KEY AUTOINCREMENT,
                    email   TEXT NOT NULL,
                    password TEXT NOT NULL
              )''')
    conn.commit()
    conn.close()
    create_database

class User(UserMixin):
    def __init__(self,id, email, password):
        self.id = str(id)
        self.email = email
        self.password = password
        self.authenticated = False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT * FROM login WHERE user_id = ?", (user_id,))
    user_data = curs.fetchone()
    conn.close()

    if user_data is None:
        return None
    else:
        return User(int(user_data[0]), user_data[1], user_data[2])


