VERSION = "0.0.1.1"

from flask import Flask
from .extensions import cors
from .routes import *
import os
import FlaskAPIServer.config

from .utils import *
from .config import *

config = FlaskAPIServer.config

logger = logger.setup(DEBUG=config.DEBUG, name="SERVER", log_path=config.LOG_PATH)

for var in config.required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Переменная окружения {var} не задана в .env")

def create_app():
    app = Flask(__name__)
    
    cors.init_app(app)

    app.register_blueprint(api)

    app.config["SECRET_KEY"] = SECRET_KEY
    setup_middleware(app)

    return app


def start_server():
    app = create_app()
    logger.info("Сервер запущен")
    app.run(port=5000, debug=config.DEBUG, host='0.0.0.0')