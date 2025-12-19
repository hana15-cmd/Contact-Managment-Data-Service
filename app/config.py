import os
from secrets import token_hex

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", token_hex(32))
    # Use env var as-is; default to /tmp/app.db if not provided
    DATABASE = os.getenv("DATABASE") or "/tmp/app.db"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"