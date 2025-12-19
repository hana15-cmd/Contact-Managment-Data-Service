from flask import Flask
from flask_login import LoginManager
from .config import BaseConfig
from .views import views
from .auth.auth import auth, seed_default_users
from app.user_auth import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id: str):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        uid = user_id
    return User.get_by_id(uid)

def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    if app.config.get("TESTING"):
        app.config.update(
            WTF_CSRF_ENABLED=False,
            SECRET_KEY=app.config.get("SECRET_KEY") or "test-secret",
        )

    login_manager.init_app(app)

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # Seed defaults at startup (idempotent)
    with app.app_context():
        seed_default_users()

    return app