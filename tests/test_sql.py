"""Импорт, целостность SQLite и пользовательские сценарии ПР7."""

import json
import sqlite3
from contextlib import closing

import pytest

import storage
from db import database
from db.import_json import import_data
from db.queries import SQL, fetch_all, fetch_one


def test_import_counts_match_source_and_is_repeatable(web):
    before = {name: fetch_one("question_summary")["total"]
              for name in ["questions"]}
    import_data(storage.DATA_DIR)
    import_data(storage.DATA_DIR)
    with closing(database.get_connection()) as connection:
        for table in ["categories", "users", "questions", "answers"]:
            source = json.loads(
                (storage.DATA_DIR / f"{table}.json").read_text(
                    encoding="utf-8"
                )
            )
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            assert count == len(source)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    assert before["questions"] == fetch_one("question_summary")["total"]


def test_import_updates_existing_ids_without_deleting_extra_rows(web):
    with closing(database.get_connection()) as connection, connection:
        connection.execute(
            "INSERT INTO categories (id, name) VALUES (?, ?)", (77, "Extra")
        )
    items = storage.load_categories()
    items[0].name = "Обновлённая тема"
    storage.save_categories(items)
    import_data(storage.DATA_DIR)
    assert fetch_one("category_detail", (1,))["name"] == "Обновлённая тема"
    assert fetch_one("category_detail", (77,))["name"] == "Extra"


def test_failed_import_rolls_back_all_tables(web):
    categories = storage.load_categories()
    categories[0].name = "Не должно сохраниться"
    storage.save_categories(categories)
    path = storage.DATA_DIR / "answers.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    items[0]["question_id"] = 999
    path.write_text(json.dumps(items), encoding="utf-8")
    with pytest.raises(sqlite3.IntegrityError):
        import_data(storage.DATA_DIR)
    assert fetch_one("category_detail", (1,))["name"] == "Python"
    assert fetch_one("answer_detail", (1,))["question_id"] == 1


def test_duplicate_json_ids_rejected_without_changing_database(web):
    path = storage.DATA_DIR / "categories.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(items + items), encoding="utf-8")
    with pytest.raises(ValueError, match="ID"):
        import_data(storage.DATA_DIR)
    assert len(fetch_all("category_list")) == 1


def test_schema_repeated_and_constraints_enforced(web):
    database.initialize_database()
    with closing(database.get_connection()) as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        result = connection.execute("PRAGMA integrity_check").fetchone()
        assert result[0] == "ok"
        for sql in [
            "UPDATE questions SET category_id = 999 WHERE id = 1",
            "UPDATE questions SET is_closed = 3 WHERE id = 1",
            "UPDATE users SET role = 'admin' WHERE id = 1",
            "DELETE FROM categories WHERE id = 1",
        ]:
            with pytest.raises(sqlite3.IntegrityError), connection:
                connection.execute(sql)
    assert fetch_one("question_summary")["total"] == 1


def test_every_catalog_query_executes_and_returns_named_rows(web):
    parameters = {
        "category_statistics": (0,),
        "question_search": ("", "", None, None, "", "", 10, 0),
        "search_count": ("", "", None, None, "", ""),
        "question_detail": (1,), "question_answers": (1,),
        "category_detail": (1,), "category_questions": (1,),
        "answer_detail": (1,),
    }
    assert len(SQL) == 18
    for name in SQL:
        rows = fetch_all(name, parameters.get(name, ()))
        for row in rows:
            assert isinstance(row, sqlite3.Row)
            assert row[row.keys()[0]] == row[0]


def test_joins_preserve_real_links(web):
    question = fetch_one("question_detail", (1,))
    answer = fetch_one("answer_detail", (1,))
    assert question["category_name"] == "Python"
    assert question["author_name"] == "Автор"
    assert answer["question_text"] == "Как работает Python?"
    assert answer["author_name"] == "Автор"


def test_left_join_zero_counts_and_having(web):
    with closing(database.get_connection()) as connection, connection:
        connection.execute(
            "INSERT INTO categories (id, name) VALUES (2, 'Web')"
        )
        connection.execute("INSERT INTO users (id, name) VALUES (2, 'Reader')")
    categories = fetch_all("category_statistics", (0,))
    assert [(r["id"], r["questions_count"]) for r in categories] == [
        (1, 1), (2, 0),
    ]
    assert len(fetch_all("category_statistics", (1,))) == 1
    assert fetch_all("category_statistics", (2,)) == []
    authors = fetch_all("author_statistics")
    assert [(r["id"], r["answers_count"]) for r in authors] == [(1, 1), (2, 0)]


@pytest.mark.parametrize("url, expected", [
    ("/questions/open/", "Как работает Python?"),
    ("/questions/unanswered/", "Вопросов пока нет"),
    ("/categories/active/", "Python"),
    ("/questions/search/", "Поиск вопросов"),
    ("/questions/statistics/", "Статистика обсуждений"),
])
def test_new_pages(web, url, expected):
    response = web.get(url)
    assert response.status_code == 200
    assert expected in response.content.decode()


def test_filters_and_unanswered_use_database(web):
    with closing(database.get_connection()) as connection, connection:
        connection.execute("UPDATE questions SET is_closed = 1 WHERE id = 1")
        connection.execute("UPDATE categories SET is_active = 0 WHERE id = 1")
    assert "Как работает Python?" not in (
        web.get("/questions/open/").content.decode()
    )
    assert "Python" not in web.get("/categories/active/").content.decode()
    with closing(database.get_connection()) as connection, connection:
        connection.execute("UPDATE questions SET is_closed = 0 WHERE id = 1")
        connection.execute("DELETE FROM answers")
    assert "Как работает Python?" in (
        web.get("/questions/unanswered/").content.decode()
    )


def test_search_combines_conditions_and_ascii_case(web):
    response = web.get("/questions/search/", {
        "q": "PYTHON", "category": "1", "since": "2026-09-19",
    })
    assert response.status_code == 200
    assert "Как работает Python?" in response.content.decode()
    response = web.get("/questions/search/", {
        "q": "Python", "since": "2027-01-01",
    })
    assert "По заданным условиям вопросов не найдено" in (
        response.content.decode()
    )


@pytest.mark.parametrize("params", [
    {"category": "abc"}, {"category": "-1"}, {"category": str(2 ** 80)},
    {"since": "2026-02-30"}, {"since": "20260101"}, {"page": "0"},
    {"page": "abc"}, {"page": "1000001"}, {"q": "x" * 201},
])
def test_invalid_search_parameters_are_400(web, params):
    response = web.get("/questions/search/", params)
    assert response.status_code == 400
    assert "Проверьте параметры" in response.content.decode()


def test_search_parameters_cannot_change_sql(web):
    response = web.get("/questions/search/", {
        "q": "' OR 1=1; DROP TABLE questions;--",
    })
    assert response.status_code == 200
    assert "По заданным условиям вопросов не найдено" in (
        response.content.decode()
    )
    assert fetch_one("question_summary")["total"] == 1


def test_search_pagination_is_stable_and_keeps_filters(web):
    with closing(database.get_connection()) as connection, connection:
        connection.executemany(
            "INSERT INTO questions (id,text,category_id,author_id,created_on) "
            "VALUES (?, ?, 1, 1, '2026-09-20')",
            [(i, f"Новый вопрос {i}") for i in range(2, 15)],
        )
    parameters = ("Новый", "Новый", 1, 1, "", "")
    first = fetch_all("question_search", (*parameters, 10, 0))
    second = fetch_all("question_search", (*parameters, 10, 10))
    assert [r["id"] for r in first] == list(range(14, 4, -1))
    assert [r["id"] for r in second] == [4, 3, 2]
    response = web.get("/questions/search/", {"q": "Новый", "category": "1"})
    assert "page=2" in response.content.decode()
    assert "category=1" in response.content.decode()


def test_statistics_empty_database_and_invalid_threshold(web):
    with closing(database.get_connection()) as connection, connection:
        connection.execute("DELETE FROM answers")
        connection.execute("DELETE FROM questions")
    assert dict(fetch_one("question_summary")) == {
        "total": 0, "open_count": 0, "closed_count": 0,
    }
    assert dict(fetch_one("answer_summary")) == {
        "total": 0, "authors_count": 0,
    }
    assert web.get("/questions/statistics/").status_code == 200
    for minimum in ["-1", "bad", str(2 ** 80)]:
        response = web.get("/questions/statistics/", {"minimum": minimum})
        assert response.status_code == 400


def test_huge_dynamic_ids_are_404(web):
    for name in ["questions", "categories", "answers"]:
        assert web.get(f"/{name}/{2 ** 80}/").status_code == 404


def test_database_path_independent_of_cwd(web, tmp_path, monkeypatch):
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    assert fetch_one("question_detail", (1,))["id"] == 1
    with closing(database.get_connection()) as connection:
        path = connection.execute("PRAGMA database_list").fetchone()[2]
        assert path == str(database.DB_PATH)
