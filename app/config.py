import os
from datetime import timedelta
from pathlib import Path

basedir = Path(__file__).resolve().parent.parent

# Force SQLite database to be created in the project root
DB_PATH = basedir / "fasttrackchef.db"


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    # Always use the project database (ignore DATABASE_URL from .env)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.as_posix()}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    UPLOAD_FOLDER = basedir / "app" / "static" / "uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    ITEMS_PER_PAGE = 12
    ADMIN_ITEMS_PER_PAGE = 10