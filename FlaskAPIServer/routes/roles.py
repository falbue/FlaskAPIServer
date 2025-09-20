from . import *
from .keys import logger


@api.route('/admin/roles', methods=['GET'])
@key_role('api_key')
def get_all_roles():
    try:
        roles = SQL_request(
            "SELECT name, priority FROM roles ORDER BY priority ASC",
            fetch='all'
        )
        return jsonify({"roles": roles}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка ролей: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route('/admin/roles', methods=['POST'])
@key_role('api_key')
def create_role():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'priority' not in data:
            return jsonify({"error": "Не указано имя или приоритет роли"}), 400

        name = data['name']
        priority = data['priority']

        SQL_request(
            "INSERT INTO roles (name, priority) VALUES (?, ?)",
            (name, priority),
            fetch=None
        )

        logger.info(f"Создана новая роль: {name} с приоритетом {priority}")
        return jsonify({"name": name, "priority": priority, "message": "Роль создана"}), 201

    except Exception as e:
        logger.error(f"Ошибка при создании роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route('/admin/roles/<name>', methods=['PATCH'])
@key_role('api_key')
def update_role(name):
    try:
        data = request.get_json()
        if not data.get("priority"):
            return jsonify({"error": "Пустое тело запроса"}), 400

        SQL_request("UPDATE roles SET priority = ? WHERE name = ?", (data.get("priority"), name), fetch=None)

        logger.info(f"Обновлена роль: {name}")
        return jsonify({"message": "Роль обновлена"}), 200

    except Exception as e:
        logger.error(f"Ошибка при обновлении роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@api.route('/admin/roles/<name>', methods=['DELETE'])
@key_role('api_key')
def delete_role(name):
    try:
        SQL_request(
            "DELETE FROM roles WHERE name = ?",
            (name,),
            fetch=None
        )

        logger.info(f"Удалена роль: {name}")
        return jsonify({"message": "Роль удалена"}), 200

    except Exception as e:
        logger.error(f"Ошибка при удалении роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500