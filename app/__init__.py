import os
from flask import Flask
from app.user_auth import User
from .views import views
from .auth.auth import auth
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hellohello'
    app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'database.db')),
    SECRET_KEY=['hihihi']))
    
    login_manager = LoginManager()

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    return app
