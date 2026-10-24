"""Проверка поведения шаблонов и подключения статики ПР6."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queryflow.settings")
django.setup()

from django.contrib.staticfiles import finders  # noqa: E402
from django.template.loader import render_to_string  # noqa: E402


def test_missing_variable_and_default():
    html = render_to_string("404.html", {})
    assert "Страница не найдена" in html
    assert "None" not in html


def test_included_status_handles_all_states():
    name = "questions/includes/question_status.html"
    for closed, count, expected in [
        (True, 0, "закрыт"), (False, 0, "ожидает ответа"),
        (False, 2, "открыт"),
    ]:
        html = render_to_string(name, {
            "question": {"is_closed": closed}, "answers_count": count,
        })
        assert expected in html


def test_child_inherits_title_navigation_and_static():
    html = render_to_string("homepage/index.html")
    assert "<title>Главная | QueryFlow</title>" in html
    assert 'aria-label="Основная навигация"' in html
    for path in ["css/style.css", "js/main.js", "img/logo.svg"]:
        assert f"/static/homepage/{path}" in html
        assert finders.find(f"homepage/{path}") is not None


def test_error_message_is_autoescaped():
    html = render_to_string("404.html", {"message": "<script>x</script>"})
    assert "<script>x</script>" not in html
    assert "&lt;script&gt;x&lt;/script&gt;" in html
