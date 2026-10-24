"""Атомарный повторяемый импорт JSON: python -m db.import_json."""

import json
from contextlib import closing
from pathlib import Path

from db.database import BASE_DIR, get_connection, initialize_database

# Имена таблиц и полей заданы разработчиком, не поступают от пользователя.
IMPORTS = {
    "categories": (
        "id", "name", "is_active",
    ),
    "users": (
        "id", "name", "role",
    ),
    "questions": (
        "id", "text", "category_id", "author_id", "is_closed", "created_on",
    ),
    "answers": (
        "id", "text", "question_id", "author_id", "created_on",
    ),
}


def import_data(data_dir=None, db_path=None):
    """Обновить записи по ID; посторонние записи базы не удалять.

    Все четыре таблицы импортируются одной транзакцией. Ошибка чтения,
    дубликат ID в JSON или нарушение FK не допускает частичного импорта.
    """
    data_dir = Path(data_dir) if data_dir is not None else BASE_DIR / "data"
    batches = {}
    for table, fields in IMPORTS.items():
        items = json.loads(
            (data_dir / f"{table}.json").read_text(encoding="utf-8")
        )
        if not isinstance(items, list):
            raise ValueError(f"{table}.json должен содержать список")
        seen = set()
        rows = []
        for item in items:
            if type(item["id"]) is not int or item["id"] in seen:
                raise ValueError(f"Некорректный или повторный ID: {table}")
            seen.add(item["id"])
            for field in ("is_active", "is_closed"):
                if field in fields:
                    if type(item[field]) is not bool:
                        raise ValueError(f"{table}.{field}: ожидается bool")
                    item[field] = int(item[field])
            rows.append(tuple(item[field] for field in fields))
        batches[table] = rows

    initialize_database(db_path)
    with closing(get_connection(db_path)) as connection:
        with connection:
            for table, fields in IMPORTS.items():
                placeholders = ", ".join("?" for _ in fields)
                updates = ", ".join(
                    f"{field}=excluded.{field}" for field in fields[1:]
                )
                sql = (
                    f"INSERT INTO {table} ({', '.join(fields)}) "
                    f"VALUES ({placeholders}) ON CONFLICT(id) "
                    f"DO UPDATE SET {updates}"
                )
                connection.executemany(sql, batches[table])
    return {table: len(rows) for table, rows in batches.items()}


if __name__ == "__main__":
    for table, count in import_data().items():
        print(f"{table}: импортировано {count}")
