from flask import current_app
from flask_login import UserMixin
import sqlite3 as sql
from werkzeug.security import check_password_hash  # For securely checking passwords

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
    def get_by_field(field, value):
        """Generalized method to fetch a user by any field."""
        with sql.connect(current_app.config['DATABASE']) as con:
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(f"SELECT * FROM users WHERE {field} = ?", (value,))
            user_data = cur.fetchone()
            if user_data:
                return User(user_data['id'], user_data['email'], user_data['password'],
                            user_data['first_name'], user_data['is_admin'])
        return None

    @staticmethod
    def get_by_id(user_id):
        return User.get_by_field('id', user_id)

    @staticmethod
    def get_by_email(email):
        return User.get_by_field('email', email)

    def check_password(self, password):
        """Verify the password provided by the user."""
        return check_password_hash(self.password, password)  # Use werkzeug.security to check password hashes
