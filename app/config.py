import os
from secrets import token_hex

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", token_hex(32))
    DATABASE = os.path.join(os.path.dirname(__file__), os.getenv("DATABASE", "database.db"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"