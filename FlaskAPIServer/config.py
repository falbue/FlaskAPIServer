import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    env_template = """SECRET_KEY=FlaskAPIServer
DB_PATH=data/database.db
LOG_PATH=data/
JWT_LIFETIME=24
DEBUG=True

PREFIX_KEY_ROLES=/admin/key_roles
PREFIX_KEYS=/admin/keys

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


CONVERSIONS = {
    'DEBUG': lambda x: x.lower() in ['true', '1']
}

for key, value in os.environ.items():
    if key in CONVERSIONS:
        globals()[key] = CONVERSIONS[key](os.getenv(key, value))
    else:
        globals()[key] = os.getenv(key)

db_dir = os.path.dirname(DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

logs = os.path.dirname(LOG_PATH)
if logs:
    os.makedirs(logs, exist_ok=True)

required_env_vars = ["SECRET_KEY", "DB_PATH", "LOG_PATH", "JWT_LIFETIME", "DEBUG"]