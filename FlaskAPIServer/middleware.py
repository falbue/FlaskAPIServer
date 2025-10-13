from functools import wraps
import time
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, g, current_app

from .utils.database import SQL_request
from .utils import logger
from . import config

logger = logger.setup(config.DEBUG, name="MIDDLEWARE", log_path=config.LOG_PATH)

_api_keys_cache = {}
_cache_last_updated = 0
CACHE_TTL = 300

# Добавляем кеш для иерархии ролей
_roles_hierarchy_cache = None

# Секретный ключ для JWT (лучше хранить в конфиге)
JWT_SECRET = config.SECRET_KEY
JWT_LIFETIME = config.JWT_LIFETIME
JWT_ALGORITHM = 'HS256'

def refresh_api_keys():
    _refresh_api_keys_cache()
    return True

def _refresh_api_keys_cache():
    global _api_keys_cache, _cache_last_updated, _roles_hierarchy_cache
    
    try:
        # Загружаем ключи и роли
        result = SQL_request(
            "SELECT ak.key, ak.role, r.priority FROM api_keys ak "
            "JOIN key_roles r ON ak.role = r.name WHERE ak.is_active = 1",
            fetch='all'
        )
        
        if result:
            _api_keys_cache = {item['key']: {'role': item['role'], 'priority': item['priority']} for item in result}
            _cache_last_updated = time.time()
            logger.info(f"Обновлен кеш API-ключей. Загружено ключей: {len(_api_keys_cache)}")
        else:
            logger.warning("Не найдено активных API-ключей в базе данных")
            
        # Загружаем иерархию ролей
        roles_result = SQL_request(
            "SELECT name, priority FROM key_roles ORDER BY priority DESC",
            fetch='all'
        )
        if roles_result:
            _roles_hierarchy_cache = {role['name']: role['priority'] for role in roles_result}
            logger.info(f"Обновлена иерархия ролей: {_roles_hierarchy_cache}")
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из базы: {e}")

def _get_api_key_info(api_key):
    global _cache_last_updated
    
    if not _api_keys_cache or time.time() - _cache_last_updated > CACHE_TTL:
        _refresh_api_keys_cache()
    
    if api_key in _api_keys_cache:
        return _api_keys_cache[api_key]
    
    try:
        result = SQL_request(
            "SELECT ak.role, r.priority FROM api_keys ak "
            "JOIN key_roles r ON ak.role = r.name "
            "WHERE ak.key = ? AND ak.is_active = 1",
            (api_key,),
            fetch='one'
        )
        
        if result:
            role_info = {'role': result['role'], 'priority': result['priority']}
            _api_keys_cache[api_key] = role_info
            return role_info
    
    except Exception as e:
        logger.error(f"Ошибка при проверке API-ключа в базе: {e}")
    
    return None

def _get_jwt_role_info(role_name):
    """Получает информацию о роли из кэша для JWT токенов"""
    if not _roles_hierarchy_cache:
        _refresh_api_keys_cache()
    
    if role_name in _roles_hierarchy_cache:
        return {
            'role': role_name,
            'priority': _roles_hierarchy_cache[role_name]
        }
    return None

def _decode_jwt_token(token):
    """Декодирует JWT токен и возвращает информацию о пользователе"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Проверяем срок действия
        if 'exp' in payload and payload['exp'] < time.time():
            return None
        
        role_name = payload.get('role')
        if not role_name:
            return None
            
        role_info = _get_jwt_role_info(role_name)
        if not role_info:
            return None
            
        return role_info
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT токен просрочен")
        return None
    except jwt.InvalidTokenError:
        logger.error("Невалидный JWT токен")
        return None

def _check_role_access(user_priority, required_priority, check_mode):
    """Проверяет доступ в зависимости от режима проверки"""
    if check_mode == 'exact':
        return user_priority == required_priority
    elif check_mode == 'min':
        return user_priority >= required_priority
    return False

def generate_jwt_token(role='min', jwt_data=None, lifetime=JWT_LIFETIME):
    """
    Генерирует JWT токен для указанной роли

    :param role: Название роли (должна существовать в базе данных)
    :param jwt_data: Словарь с дополнительными данными для записи в токен
    """
    if jwt_data is None:
        jwt_data = {}

    if not _roles_hierarchy_cache:
        _refresh_api_keys_cache()

    if role == "min": # Находим роль с минимальным значением
        role = min(_roles_hierarchy_cache, key=_roles_hierarchy_cache.get)

    if role not in _roles_hierarchy_cache:
        raise ValueError(f"Роль '{role}' не существует в системе")

    print(lifetime)
    payload = {
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=int(lifetime)),
        'iat': datetime.utcnow()
    }

    # Добавляем дополнительные данные в payload
    payload.update(jwt_data)

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt_token(token):  # Декодирует JWT токен и возвращает его содержимое
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Токен просрочен")
    except jwt.InvalidTokenError:
        raise ValueError("Некорректный токен")

def key_role(required_role=None, check_mode='min'):
    """
    Декоратор для проверки ролей с поддержкой иерархии или приоритета
    
    :param required_role: Требуемая роль (строка) или приоритет (число)
    :param check_mode: Режим проверки:
        - 'min': минимальная требуемая роль или приоритет (по умолчанию)
        - 'exact': точное совпадение
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            auth_header = request.headers.get('Authorization')
            
            # Проверяем JWT токен (если API ключ не предоставлен)
            if not api_key and auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                key_info = _decode_jwt_token(token)
                
                if not key_info:
                    return jsonify({"error": "Невалидный JWT токен"}), 403
                
                user_role = key_info['role']
                user_priority = key_info['priority']
                
                # Помечаем, что использовался JWT
                g.auth_method = 'jwt'
                
            # Проверяем API ключ
            elif api_key:
                key_info = _get_api_key_info(api_key)
                
                if not key_info:
                    return jsonify({"error": "Неверный API ключ"}), 403
                
                user_role = key_info['role']
                user_priority = key_info['priority']
                
                # Помечаем, что использовался API ключ
                g.auth_method = 'api_key'
                
            else:
                return jsonify({"error": "API ключ или JWT токен отсутствует"}), 401

            # Проверка по приоритету или роли
            if required_role is not None:
                # Если передано число — работаем с приоритетом
                if isinstance(required_role, (int, float)):
                    required_priority = required_role
                # Если строка — получаем приоритет из кэша
                elif isinstance(required_role, str):
                    if not _roles_hierarchy_cache:
                        _refresh_api_keys_cache()
                    
                    required_priority = _roles_hierarchy_cache.get(required_role)
                    if required_priority is None:
                        return jsonify({"error": "Требуемая роль не найдена"}), 500
                else:
                    return jsonify({"error": "Неверный формат required_role"}), 500

                # Проверка доступа
                if not _check_role_access(user_priority, required_priority, check_mode):
                    return jsonify({"error": "Недостаточно прав"}), 403

            # Сохраняем данные в g
            g.api_key = api_key if api_key else None
            g.jwt_token = auth_header.split(' ')[1] if auth_header and auth_header.startswith('Bearer ') else None
            g.api_key_role = user_role
            g.api_key_priority = user_priority
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def setup_middleware(app):
    app.config['ROLES_HIERARCHY'] = _roles_hierarchy_cache

# Функции для внешнего использования
def get_available_roles():
    """Возвращает доступные роли"""
    if not _roles_hierarchy_cache:
        _refresh_api_keys_cache()
    return _roles_hierarchy_cache