import os
from secrets import token_hex


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    DATABASE = os.getenv("DATABASE", "/data/app.db")  # use Render Disk at /data
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"