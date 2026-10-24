"""Изолированные данные и отдельная SQLite-база для веб-тестов."""

import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queryflow.settings")
django.setup()

from django.test import Client, override_settings  # noqa: E402

import storage  # noqa: E402
from db import database  # noqa: E402
from db.import_json import import_data  # noqa: E402
from models.answers import Answer  # noqa: E402
from models.categories import Category  # noqa: E402
from models.questions import Question  # noqa: E402
from models.users import User  # noqa: E402


@pytest.fixture
def web(tmp_path, monkeypatch):
    """Каждый тест читает и пишет только во временный каталог."""
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "queryflow.sqlite")
    category = Category(1, "Python")
    user = User(1, "Автор", "user")
    question = Question(1, "Как работает Python?", category, user,
                        created_on="2026-09-19")
    answer = Answer(1, "Через интерпретатор.", question, user,
                    created_on="2026-09-19")
    storage.save_categories([category])
    storage.save_users([user])
    storage.save_questions([question])
    storage.save_answers([answer])
    import_data(tmp_path)
    with override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"]):
        yield Client()
