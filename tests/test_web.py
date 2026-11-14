"""HTTP-проверки ПР5–ПР7 с отдельной временной предметной базой."""

import os
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
from answers.models import Answer  # noqa: E402
from categories.models import Category  # noqa: E402
from participants.models import User  # noqa: E402
from questions.models import Question  # noqa: E402


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
    ("/questions/999/", "Страница не найдена"),
    ("/categories/999/", "Страница не найдена"),
    ("/answers/999/", "Страница не найдена"),
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
        assert b"No Question matches" in response.content


def test_http404_exception_uses_root_handler(web, monkeypatch):
    def missing(*args, **kwargs):
        raise Http404("Internal message must not be rendered")

    monkeypatch.setattr("questions.views.get_object_or_404", missing)
    response = web.get("/questions/1/")
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()
    assert b"Internal message" not in response.content


@pytest.mark.parametrize("field", ["text", "category", "author"])
def test_model_text_is_escaped(web, field):
    payload = '<script>alert("xss")</script>'
    if field == "text":
        Question.objects.filter(pk=1).update(text=payload)
    elif field == "category":
        Category.objects.filter(pk=1).update(name=payload)
    else:
        User.objects.filter(pk=1).update(name=payload)
    for url in ["/questions/", "/questions/1/"]:
        body = web.get(url).content.decode()
        assert payload not in body
        assert escape(payload) in body


def test_answer_text_is_escaped(web):
    payload = '<img src=x onerror="alert(1)">'
    Answer.objects.filter(pk=1).update(text=payload)
    for url in ["/answers/", "/answers/1/", "/questions/1/"]:
        body = web.get(url).content.decode()
        assert payload not in body
        assert escape(payload) in body


def test_empty_storage_has_readable_pages(web):
    for model in (Answer, Question, User, Category):
        model.objects.all().delete()
    for url in ["/questions/", "/categories/", "/answers/"]:
        response = web.get(url)
        assert response.status_code == 200
        assert "пока нет" in response.content.decode()


def test_status_and_orm_changes_are_visible_on_next_request(web):
    assert "открыт" in web.get("/questions/1/").content.decode()
    Answer.objects.all().delete()
    assert "ожидает ответа" in web.get("/questions/1/").content.decode()
    Question.objects.filter(pk=1).update(
        status=Question.Status.CLOSED, text="Обновлённый вопрос из ORM")
    body = web.get("/questions/1/").content.decode()
    assert "закрыт" in body
    assert "Обновлённый вопрос из ORM" in body


def test_inactive_category_is_displayed_and_get_does_not_write(web):
    Category.objects.filter(pk=1).update(is_active=False)
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
