import os
from pathlib import Path

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10.0"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
