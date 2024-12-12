from flask import current_app
from flask_login import UserMixin
import sqlite3 as sql


class User(UserMixin):
    def __init__(self, id, email, password, first_name, is_admin):
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)  # Flask-Login needs this method to identify the user

    @staticmethod
    def get_by_id(user_id):
        con = sql.connect(current_app.config['DATABASE'])
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cur.fetchone()
        con.close()
        if user_data:
            # Include additional fields if needed (like first_name, is_admin)
            return User(user_data['id'], user_data['email'], user_data['password'], user_data['first_name'],
                        user_data['is_admin'])
        return None

    @staticmethod
    def get_by_email(email):
        con = sql.connect(current_app.config['DATABASE'])
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cur.fetchone()
        con.close()
        if user_data:
            # Return user object with necessary fields
            return User(user_data['id'], user_data['email'], user_data['password'], user_data['first_name'],
                        user_data['is_admin'])
        return None
