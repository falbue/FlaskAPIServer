import os
import importlib
from flask import Blueprint, jsonify, request, abort, g
from functools import wraps
from FlaskAPIServer.middleware import setup_middleware, key_role, refresh_api_keys
import io
from FlaskAPIServer.utils.utils import *
from FlaskAPIServer.utils.database import SQL_request
import FlaskAPIServer.utils.logger
import uuid

logger = FlaskAPIServer.utils.logger.setup(name="ROUTES")

api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def example():
    return jsonify({"message": "API Работает"}), 200


def import_modules_from_directory(directory, package_name):
    """Рекурсивно импортирует все модули из директории и поддиректорий"""
    imported_modules = []
    
    for root, dirs, files in os.walk(directory):
        # Пропускаем __pycache__ и другие служебные директории
        dirs[:] = [d for d in dirs if not d.startswith('_') and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                # Получаем относительный путь для импорта
                rel_path = os.path.relpath(root, directory)
                if rel_path == '.':
                    module_path = f'.{file[:-3]}'
                else:
                    # Преобразуем путь в формат для импорта (заменяем / на .)
                    rel_module_path = rel_path.replace(os.sep, '.')
                    module_path = f'.{rel_module_path}.{file[:-3]}'
                
                try:
                    module = importlib.import_module(module_path, package_name)
                    imported_modules.append(module)
                    
                    # Импортируем все публичные имена из модуля
                    for name in dir(module):
                        if not name.startswith('_'):
                            globals()[name] = getattr(module, name)
                            if '__all__' not in globals():
                                globals()['__all__'] = []
                            globals()['__all__'].append(name)
                            
                except ImportError as e:
                    print(f"Ошибка импорта модуля {module_path}: {e}")
    
    return imported_modules

if __name__ == "routes":
    print(__name__)
    package_dir = os.path.dirname(__file__)
    import_modules_from_directory(package_dir, __package__)