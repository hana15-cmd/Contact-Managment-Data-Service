import os
from flask import Flask, g
import sqlite3
from .views import views

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hellohello'
    app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'database.db')),
    SECRET_KEY=['hihihi']))

    app.register_blueprint(views, url_prefix='/')
    # app.register_blueprint(auth, url_prefix='/')

    return app