"""Исполнение именованных запросов из единого sql/queries.sql."""

from contextlib import closing

from db.database import BASE_DIR, get_connection


def load_queries():
    text = (BASE_DIR / "sql" / "queries.sql").read_text(encoding="utf-8")
    queries = {}
    for section in text.split("-- name: ")[1:]:
        name, sql = section.split("\n", 1)
        queries[name.strip()] = sql.strip()
    return queries


SQL = load_queries()


def fetch_all(name, parameters=()):
    with closing(get_connection()) as connection:
        return connection.execute(SQL[name], parameters).fetchall()


def fetch_one(name, parameters=()):
    with closing(get_connection()) as connection:
        return connection.execute(SQL[name], parameters).fetchone()
