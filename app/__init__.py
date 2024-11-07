from flask import Flask, request, session, g, redirect, url_for, render_template, flash
import sqlite3
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hellohello'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')  # Set a URL prefix if desired

    return app




