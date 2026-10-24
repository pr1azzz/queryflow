"""HTTP-проверки ПР5–ПР7 с отдельной временной предметной базой."""

import os
from contextlib import closing
from html import escape

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queryflow.settings")
django.setup()

from django.http import Http404  # noqa: E402
from django.test import override_settings  # noqa: E402
from django.urls import Resolver404, resolve, reverse  # noqa: E402

import storage  # noqa: E402
from db import database  # noqa: E402
from db.import_json import import_data  # noqa: E402


@pytest.mark.parametrize("url, expected", [
    ("/", "Знания начинаются с вопроса"),
    ("/questions/", "Как работает Python?"),
    ("/questions/1/", "Через интерпретатор."),
    ("/categories/", "Python"),
    ("/categories/1/", "Как работает Python?"),
    ("/answers/", "Через интерпретатор."),
    ("/answers/1/", "Как работает Python?"),
])
def test_pages_use_sqlite_and_shared_html(web, url, expected):
    response = web.get(url)
    body = response.content.decode()
    assert response.status_code == 200
    assert response["Content-Type"] == "text/html; charset=utf-8"
    assert expected in body
    assert '<html lang="ru">' in body
    assert 'name="viewport"' in body
    assert "bootstrap@5.3.3" in body
    for target in ["/", "/questions/", "/categories/", "/answers/"]:
        assert f'href="{target}"' in body


@pytest.mark.parametrize("url, expected", [
    ("/questions/999/", "Вопрос не найден"),
    ("/categories/999/", "Категория не найдена"),
    ("/answers/999/", "Ответ не найден"),
    ("/nonexistent/", "Страница не найдена"),
    ("/questions/abc/", "Страница не найдена"),
    ("/questions/-1/", "Страница не найдена"),
    ("/categories/abc/", "Страница не найдена"),
    ("/answers/abc/", "Страница не найдена"),
])
def test_missing_resources_and_routes(web, url, expected):
    response = web.get(url)
    assert response.status_code == 404
    assert expected in response.content.decode()


def test_converter_passes_integer_and_names_reverse(web):
    match = resolve("/questions/123/")
    assert match.view_name == "questions:detail"
    assert match.kwargs == {"question_id": 123}
    assert reverse("questions:detail", args=[123]) == "/questions/123/"
    with pytest.raises(Resolver404):
        resolve("/questions/abc/")


def test_debug_affects_route_404_but_not_explicit_response(web):
    with override_settings(DEBUG=True):
        assert b"Using the URLconf" in web.get("/nonexistent/").content
        response = web.get("/questions/999/")
        assert response.status_code == 404
        assert "Вопрос не найден" in response.content.decode()


def test_http404_exception_uses_root_handler(web, monkeypatch):
    def missing(*args):
        raise Http404("Internal message must not be rendered")

    monkeypatch.setattr("questions.views.fetch_one", missing)
    response = web.get("/questions/1/")
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()
    assert b"Internal message" not in response.content


@pytest.mark.parametrize("field", ["text", "category", "author", "date"])
def test_json_text_is_escaped(web, field):
    payload = '<script>alert("xss")</script>'
    categories = storage.load_categories()
    users = storage.load_users()
    questions = storage.load_questions(categories, users)
    if field == "text":
        questions[0].text = payload
        storage.save_questions(questions)
    elif field == "category":
        categories[0].name = payload
        storage.save_categories(categories)
    elif field == "author":
        users[0].name = payload
        storage.save_users(users)
    else:
        questions[0].created_on = payload
        storage.save_questions(questions)
    import_data(storage.DATA_DIR)
    for url in ["/questions/", "/questions/1/"]:
        body = web.get(url).content.decode()
        assert payload not in body
        assert escape(payload) in body


def test_answer_text_is_escaped(web):
    categories = storage.load_categories()
    users = storage.load_users()
    questions = storage.load_questions(categories, users)
    answers = storage.load_answers(questions, users)
    answers[0].text = '<img src=x onerror="alert(1)">'
    storage.save_answers(answers)
    import_data(storage.DATA_DIR)
    for url in ["/answers/", "/answers/1/", "/questions/1/"]:
        body = web.get(url).content.decode()
        assert answers[0].text not in body
        assert escape(answers[0].text) in body


def test_empty_storage_has_readable_pages(web):
    with closing(database.get_connection()) as connection, connection:
        for table in ["answers", "questions", "users", "categories"]:
            connection.execute(f"DELETE FROM {table}")
    for url in ["/questions/", "/categories/", "/answers/"]:
        response = web.get(url)
        assert response.status_code == 200
        assert "пока нет" in response.content.decode()


def test_status_and_sql_changes_are_visible_on_next_request(web):
    assert "открыт" in web.get("/questions/1/").content.decode()
    with closing(database.get_connection()) as connection, connection:
        connection.execute("DELETE FROM answers")
    assert "ожидает ответа" in web.get("/questions/1/").content.decode()
    with closing(database.get_connection()) as connection, connection:
        connection.execute(
            "UPDATE questions SET is_closed = 1, text = ? WHERE id = 1",
            ("Обновлённый вопрос из SQLite",),
        )
    body = web.get("/questions/1/").content.decode()
    assert "закрыт" in body
    assert "Обновлённый вопрос из SQLite" in body


def test_inactive_category_is_displayed_and_get_does_not_write(web):
    categories = storage.load_categories()
    categories[0].is_active = False
    storage.save_categories(categories)
    import_data(storage.DATA_DIR)
    before = {p.name: p.read_bytes() for p in storage.DATA_DIR.glob("*.json")}
    database_before = database.DB_PATH.read_bytes()
    for url in ["/", "/questions/", "/questions/1/", "/categories/",
                "/categories/1/", "/answers/", "/answers/1/"]:
        assert web.get(url).status_code == 200
    assert "Архив" in web.get("/categories/1/").content.decode()
    after = {p.name: p.read_bytes() for p in storage.DATA_DIR.glob("*.json")}
    assert before == after
    assert database_before == database.DB_PATH.read_bytes()


def test_untrusted_host_is_rejected(web):
    assert web.get("/", HTTP_HOST="example.invalid").status_code == 400


def test_head_response_has_no_body(web):
    response = web.head("/questions/1/")
    assert response.status_code == 200
    assert response.content == b""
