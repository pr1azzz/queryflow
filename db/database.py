"""Подключение и создание базы предметной области QueryFlow."""

import sqlite3
from contextlib import closing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "queryflow.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(db_path=None, *, create=False):
    """Открыть нужный файл, включить FK и именованные строки результата."""
    path = Path(db_path if db_path is not None else DB_PATH).resolve()
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    uri = path.as_uri() + ("?mode=rwc" if create else "?mode=rw")
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path=None):
    """Создать базу и применить идемпотентную схему без удаления данных."""
    with closing(get_connection(db_path, create=True)) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    initialize_database()
    print(f"Схема создана: {DB_PATH}")
