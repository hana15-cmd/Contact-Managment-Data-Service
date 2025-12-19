import os
import sqlite3 as sql
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import SignupForm
from app.database_logic.models import add_entry
from app.user_auth import User

auth = Blueprint('auth', __name__)

# Load secrets from a gitignored local file if present, else from env
try:
    from app.local_secrets import (
        DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASSWORD,
        DEFAULT_USER_EMAIL, DEFAULT_USER_NAME, DEFAULT_USER_PASSWORD,
    )
except ImportError:
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
    DEFAULT_ADMIN_NAME = os.getenv("DEFAULT_ADMIN_NAME", "Admin")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL")
    DEFAULT_USER_NAME = os.getenv("DEFAULT_USER_NAME", "Regular")
    DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD")

DEFAULT_ADMIN = {
    "email": (DEFAULT_ADMIN_EMAIL or "").strip().lower(),
    "first_name": DEFAULT_ADMIN_NAME,
    "password": DEFAULT_ADMIN_PASSWORD,
    "is_admin": True,
}
DEFAULT_USER = {
    "email": (DEFAULT_USER_EMAIL or "").strip().lower(),
    "first_name": DEFAULT_USER_NAME,
    "password": DEFAULT_USER_PASSWORD,
    "is_admin": False,
}

def _looks_hashed(pw: str) -> bool:
    return isinstance(pw, str) and pw.startswith(("pbkdf2:", "scrypt:", "argon2:"))

def _set_hashed_password(user_id: int, raw_password: str):
    hashed = generate_password_hash(raw_password)
    with sql.connect(current_app.config['DATABASE']) as con:
        cur = con.cursor()
        cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        con.commit()

def seed_default_users():
    """Ensure default admin/user exist and have hashed passwords."""
    try:
        for u in (DEFAULT_ADMIN, DEFAULT_USER):
            user = User.get_by_email(u["email"])
            if not user:
                add_entry(u["email"], u["first_name"], u["password"], u["is_admin"])
                user = User.get_by_email(u["email"])
                current_app.logger.info(f"Seeded default user: {u['email']}")

            # If the password in DB is plaintext (e.g., after reset), hash it once
            if user and not _looks_hashed(user.password):
                _set_hashed_password(user.id, u["password"])
                current_app.logger.info(f"Normalized password hash for: {u['email']}")
    except Exception as e:
        current_app.logger.warning(f"Default user seeding skipped: {e}")

@auth.before_app_request
def ensure_seeded_once():
    if not current_app.config.get("_DEFAULT_USERS_SEEDED", False):
        seed_default_users()
        current_app.config["_DEFAULT_USERS_SEEDED"] = True

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        password = form.password.data
        user_type = form.user_type.data

        is_admin = (user_type == 'admin')
        result = add_entry(email, first_name, password, is_admin)

        if result == 'success':
            flash('Registration successful! Please log in.', category='success')
            return redirect(url_for('auth.login'))
        elif isinstance(result, tuple) and result[0] == 'email_taken':
            flash("Email is already taken by user. Please use a different one.", category='danger')
        else:
            flash('An unexpected error occurred. Please try again.', category='danger')

    return render_template('auth/signup.html', form=form)

@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.get_by_email(email)

        valid = False
        if user:
            if _looks_hashed(user.password):
                valid = check_password_hash(user.password, password)
            else:
                # Fallback for plaintext after DB reset; also normalize to hash
                valid = (user.password == password)
                if valid:
                    _set_hashed_password(user.id, password)

        if valid:
            login_user(user)
            session['user_id'] = user.id
            session['user_name'] = user.first_name
            session['is_admin'] = user.is_admin
            flash('You were successfully logged in', category='success')
            return redirect(url_for('views.contacts'))
        else:
            flash('Invalid username or password', category='error')

    return render_template('auth/login.html')

@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('is_admin', None)
    flash('You were successfully logged out', category='success')
    return redirect(url_for('auth.login'))