import json
import sqlite3
from .. import config


def SQL_request(
    query: str, params: tuple = (), fetch: str | None = "one"
) -> (
    dict[str, str | int | float | bool | None]
    | list[dict[str, str | int | float | bool | None]]
    | None
):
    """Выполняет SQL-запрос к базе данных

    Возвращает:
    - при `fetch == "one"`: `dict[str, Any] | None`
    - при `fetch == "all"`: `list[dict[str, Any]]`
    - в остальных случаях: `None` (коммит)"""

    def _parse_json_if_needed(value):
        if isinstance(value, str):
            value = value.strip()
            if value.startswith(("{", "[")):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
        return value

    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)

            if fetch == "all":
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                result = [
                    {
                        col: _parse_json_if_needed(row[i])
                        for i, col in enumerate(columns)
                    }
                    for row in rows
                ]

            elif fetch == "one":
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = {
                        col: _parse_json_if_needed(row[i])
                        for i, col in enumerate(columns)
                    }
                else:
                    result = None
            else:
                conn.commit()
                result = None

        except sqlite3.Error as e:
            print(f"Ошибка SQL: {e}")
            raise

    return result


SQL_request("""CREATE TABLE IF NOT EXISTS api_keys (
    key TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

SQL_request("""CREATE TABLE IF NOT EXISTS key_roles (
    name VARCHAR(50) PRIMARY KEY,
    priority INTEGER NOT NULL UNIQUE
);""")

SQL_request("INSERT OR IGNORE INTO key_roles (name, priority) VALUES ('api_key', 10);")
