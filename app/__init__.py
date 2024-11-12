# __init__.py
from flask import Flask, g
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hellohello'

    from .views import views
  
    app.register_blueprint(views, url_prefix='/')
    # app.register_blueprint(auth, url_prefix='/')

    return app
