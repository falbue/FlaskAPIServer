import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
DB_PATH = os.getenv("DB_PATH")
LOG_PATH = os.getenv("LOG_PATH")
JWT_ACCESS_EXPIRES_HOURS = int(os.getenv("JWT_ACCESS_EXPIRES_HOURS", "24"))
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]

db_dir = os.path.dirname(DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

logs = os.path.dirname(LOG_PATH)
if logs:
    os.makedirs(logs, exist_ok=True)