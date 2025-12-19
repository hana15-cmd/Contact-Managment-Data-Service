import os
import sqlite3 as sql
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import SignupForm
from app.database_logic.models import add_entry, init_db_scheme
from app.user_auth import User

auth = Blueprint('auth', __name__)

def load_defaults():
    """Load default credentials from local_secrets.py or environment."""
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

    admin = {
        "email": (DEFAULT_ADMIN_EMAIL or "").strip(),   # preserve capitalization
        "first_name": DEFAULT_ADMIN_NAME,
        "password": DEFAULT_ADMIN_PASSWORD,
        "is_admin": True,
    }
    user = {
        "email": (DEFAULT_USER_EMAIL or "").strip(),    # preserve capitalization
        "first_name": DEFAULT_USER_NAME,
        "password": DEFAULT_USER_PASSWORD,
        "is_admin": False,
    }
    return admin, user

DEFAULT_ADMIN, DEFAULT_USER = load_defaults()

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
            email = (u["email"] or "").strip()
            pwd = (u["password"] or "").strip()
            if not email or not pwd:
                current_app.logger.info(f"[seed] skip: missing email/password for {u}")
                continue

            user = User.get_by_email(email)
            if not user:
                result = add_entry(email, u["first_name"], pwd, u["is_admin"])
                current_app.logger.info(f"[seed] add_entry({email}) -> {result}")
                user = User.get_by_email(email)

            if user and not _looks_hashed(user.password):
                _set_hashed_password(user.id, pwd)
                current_app.logger.info(f"[seed] normalized hash for {email}")
    except Exception as e:
        current_app.logger.warning(f"[seed] failed: {e}")

@auth.before_app_request
def bootstrap():
    """Create schema once, then seed defaults (runs once per process)."""
    if not current_app.config.get("_BOOTSTRAPPED", False):
        try:
            init_db_scheme()
        except Exception as e:
            current_app.logger.warning(f"[schema] init failed: {e}")
        seed_default_users()
        current_app.config["_BOOTSTRAPPED"] = True

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = (form.email.data or "").strip()  # keep capitalization
        first_name = form.first_name.data
        password = form.password.data
        is_admin = (form.user_type.data == 'admin')

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
        email = (request.form.get('email') or "").strip()  # keep capitalization
        password = request.form.get('password') or ""

        user = User.get_by_email(email)
        valid = False
        if user:
            if _looks_hashed(user.password):
                valid = check_password_hash(user.password, password)
            else:
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