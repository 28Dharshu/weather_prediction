import os
from pathlib import Path

# Base directory of the python_app
BASE_DIR = Path(__file__).resolve().parent

# Auto-load .env file if present
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    with open(_env_file, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # DB_TYPE: 'postgres' or 'mongodb'
    DB_TYPE = os.environ.get("DB_TYPE", "postgres").lower().strip()
    
    # PostgreSQL / SQLAlchemy settings
    # If DATABASE_URL is set, use it. Otherwise, fallback to SQLite for zero-config local testing.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    )
    # Fix postgres:// URLs if provided by older PaaS platforms (SQLAlchemy expects postgresql://)
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB settings
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/my_auth_db")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "my_auth_db")
    
    # File upload configurations
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    
    # External APIs
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
    GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "")
