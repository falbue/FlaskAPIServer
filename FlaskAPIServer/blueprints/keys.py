import uuid
from flask import Blueprint, jsonify, request

from ..utils.logger import setup as logger_setup
from .. import config
from ..middleware import role, refresh_api_keys
from ..utils.database import SQL_request as SQL

logger = logger_setup("API_KEYS", config.DEBUG, log_path=config.LOG_PATH)
PREFIX_KEYS = "/keys"

keys = Blueprint("keys", __name__, url_prefix=PREFIX_KEYS)


@keys.route("/", methods=["GET"])
@role("api_key")
def get_all_keys():
    try:
        keys = SQL(
            "SELECT key, role, is_active, created_at, updated_at FROM api_keys ORDER BY created_at DESC",
            fetch="all",
        )
        return jsonify({"data": {"keys": keys}, "success": True}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка ключей: {e}")
        return jsonify(
            {"message": "Внутренняя ошибка сервера", "success": False, "error": str(e)}
        ), 500


@keys.route("/", methods=["POST"])
@role("api_key")
def api_create_key():
    try:
        data = request.get_json()
        if not data or "role" not in data:
            return jsonify({"error": "Не указана роль ключа"}), 400

        role = data["role"]
        api_key = str(uuid.uuid4()).replace("-", "")
        SQL(
            "INSERT INTO api_keys (key, role) VALUES (?, ?)",
            (api_key, role),
            fetch=None,
        )

        refresh_api_keys()

        logger.debug(f"Создан новый API-ключ с ролью {role}")
        return jsonify(
            {
                "data": {"key": api_key, "role": role},
                "message": "Ключ создан",
                "success": True,
            }
        ), 201

    except Exception as e:
        logger.error(f"Ошибка при создании ключа: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера", "success": False}), 500


@keys.route("/<key>", methods=["PATCH"])
@role("api_key")
def update_key(key):
    try:
        data = request.get_json()

        role = data.get("role", None)
        is_active = data.get("is_active", True)
        if role:
            SQL(
                "UPDATE api_keys SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (role, key),
                fetch=None,
            )

        SQL(
            "UPDATE api_keys SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
            (is_active, key),
            fetch=None,
        )

        refresh_api_keys()

        logger.debug(f"Обновлен API-ключ {key}: роль={role}, активен={is_active}")
        return jsonify({"message": "Ключ обновлен", "success": True}), 200

    except Exception as e:
        logger.error(f"Ошибка при обновлении ключа: {e}")
        return jsonify(
            {"message": "Внутренняя ошибка сервера", "success": False, "error": str(e)}
        ), 500


@keys.route("/<key>", methods=["DELETE"])
@role("api_key")
def delete_key(key):
    try:
        SQL("DELETE FROM api_keys WHERE key = ?", (key,), fetch=None)

        refresh_api_keys()

        logger.debug(f"Удален API-ключ {key}")
        return jsonify({"message": "Ключ удален", "success": True}), 200

    except Exception as e:
        logger.error(f"Ошибка при удалении ключа: {e}")
        return jsonify(
            {"message": "Внутренняя ошибка сервера", "success": False, "error": str(e)}
        ), 500


@keys.route("/refresh", methods=["GET"])
@role("api_key")
def refresh_keys():
    try:
        refresh_api_keys()
        return jsonify({"message": "Кеш API-ключей обновлен", "success": True}), 200
    except Exception as e:
        logger.error(f"Ошибка при обновлении кеша: {e}")
        return jsonify(
            {"message": "Внутренняя ошибка сервера", "success": False, "error": str(e)}
        ), 500
