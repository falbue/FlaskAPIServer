import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    env_template = """SECRET_KEY=
DB_PATH=data/database.db
LOG_PATH=data/
JWT_LIFETIME=24
DEBUG=True

SMTP_SERVER=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=
"""
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    raise RuntimeError(
        "Файл .env не найден и был создан автоматически.\n"
        "Пожалуйста, настройте его перед запуском:\n"
        "1. Добавьте ваш SECRET_KEY в файл .env\n"
        "2. Настройте другие параметры при необходимости\n"
        "3. Перезапустите приложение\n"
        f"Файл создан по пути: {env_path.absolute()}"
    )


SECRET_KEY = os.getenv("SECRET_KEY")
DB_PATH = os.getenv("DB_PATH")
LOG_PATH = os.getenv("LOG_PATH")
JWT_LIFETIME = int(os.getenv("JWT_LIFETIME", "24"))
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]

db_dir = os.path.dirname(DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

logs = os.path.dirname(LOG_PATH)
if logs:
    os.makedirs(logs, exist_ok=True)

required_env_vars = ["SECRET_KEY", "DB_PATH", "LOG_PATH", "JWT_LIFETIME", "DEBUG"]