from flask import Blueprint, jsonify, request

from ..utils.logger import setup as logger_setup
from .. import config
from ..utils.database import SQL_request as SQL
from ..middleware import role

roles = Blueprint("roles", __name__, url_prefix="/roles")
logger = logger_setup("API_ROLES", config.DEBUG, log_path=config.LOG_PATH)


@roles.route("/", methods=["GET"])
@role("api_key")
def get_all_roles():
    try:
        roles = SQL(
            "SELECT name, priority FROM key_roles ORDER BY priority ASC", fetch="all"
        )
        return jsonify({"roles": roles}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка ролей: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@roles.route("/", methods=["POST"])
@role("api_key")
def create_role():
    try:
        data = request.get_json()
        if not data or "name" not in data or "priority" not in data:
            return jsonify({"error": "Не указано имя или приоритет роли"}), 400

        name = data["name"]
        priority = data["priority"]

        SQL(
            "INSERT INTO key_roles (name, priority) VALUES (?, ?)",
            (name, priority),
            fetch=None,
        )

        logger.info(f"Создана новая роль: {name} с приоритетом {priority}")
        return jsonify(
            {"name": name, "priority": priority, "message": "Роль создана"}
        ), 201

    except Exception as e:
        logger.error(f"Ошибка при создании роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@roles.route("/<name>", methods=["PATCH"])
@role("api_key")
def update_role(name):
    try:
        data = request.get_json()
        if not data.get("priority"):
            return jsonify({"error": "Пустое тело запроса"}), 400

        SQL(
            "UPDATE key_roles SET priority = ? WHERE name = ?",
            (data.get("priority"), name),
            fetch=None,
        )

        logger.info(f"Обновлена роль: {name}")
        return jsonify({"message": "Роль обновлена"}), 200

    except Exception as e:
        logger.error(f"Ошибка при обновлении роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@roles.route("/<name>", methods=["DELETE"])
@role("api_key")
def delete_role(name):
    try:
        SQL("DELETE FROM key_roles WHERE name = ?", (name,), fetch=None)

        logger.info(f"Удалена роль: {name}")
        return jsonify({"message": "Роль удалена"}), 200

    except Exception as e:
        logger.error(f"Ошибка при удалении роли: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500
