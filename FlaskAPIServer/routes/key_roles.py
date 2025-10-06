from . import *
from .keys import logger


@api.route('/admin/key_roles', methods=['GET'])
@key_role('api_key')
def get_all_key_roles():
    try:
        key_roles = SQL_request(
            "SELECT name, priority FROM key_roles ORDER BY priority ASC",
            fetch='all'
        )
        return jsonify({"key_roles": key_roles}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка ролей: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route('/admin/key_roles', methods=['POST'])
@key_role('api_key')
def create_role():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'priority' not in data:
            return jsonify({"error": "Не указано имя или приоритет роли"}), 400

        name = data['name']
        priority = data['priority']

        SQL_request(
            "INSERT INTO key_roles (name, priority) VALUES (?, ?)",
            (name, priority),
            fetch=None
        )

        logger.info(f"Создана новая роль: {name} с приоритетом {priority}")
        return jsonify({"name": name, "priority": priority, "message": "Роль создана"}), 201

    except Exception as e:
        logger.error(f"Ошибка при создании роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route('/admin/key_roles/<name>', methods=['PATCH'])
@key_role('api_key')
def update_role(name):
    try:
        data = request.get_json()
        if not data.get("priority"):
            return jsonify({"error": "Пустое тело запроса"}), 400

        SQL_request("UPDATE key_roles SET priority = ? WHERE name = ?", (data.get("priority"), name), fetch=None)

        logger.info(f"Обновлена роль: {name}")
        return jsonify({"message": "Роль обновлена"}), 200

    except Exception as e:
        logger.error(f"Ошибка при обновлении роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route('/admin/key_roles/<name>', methods=['DELETE'])
@key_role('api_key')
def delete_role(name):
    try:
        SQL_request(
            "DELETE FROM key_roles WHERE name = ?",
            (name,),
            fetch=None
        )

        logger.info(f"Удалена роль: {name}")
        return jsonify({"message": "Роль удалена"}), 200

    except Exception as e:
        logger.error(f"Ошибка при удалении роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500