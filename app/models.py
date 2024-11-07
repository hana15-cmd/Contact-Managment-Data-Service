from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


login_manager = LoginManager()
login_manager.login_view = 'login'
