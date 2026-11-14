"""Регрессия ПР9: связи, импорт, статистика и стоимость выборок."""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db.models.deletion import ProtectedError

from answers.models import Answer
from categories.models import Category
from db import database
from participants.models import User
from questions.models import Question
from questions.queries import question_rows, statistics_context


def test_legacy_import_preserves_links_and_local_edits(web):
    q = Question.objects.get(pk=1)
    assert q.category.name == "Python"
    assert q.author.name == "Автор"
    assert q.answers.get().question_id == q.pk
    q.text = "Отредактировано в ORM"
    q.status = Question.Status.CLOSED
    q.save()
    call_command("import_legacy", source=database.DB_PATH)
    q.refresh_from_db()
    assert q.text == "Отредактировано в ORM"
    assert Question.objects.count() == 1


def test_protected_delete_and_reverse_relations(web):
    q = Question.objects.get(pk=1)
    with pytest.raises(ProtectedError):
        q.category.delete()
    with pytest.raises(ProtectedError):
        q.delete()
    assert q.author.questions.get() == q
    assert q.author.answers.count() == 1


def test_zero_groups_and_empty_aggregates(web):
    Category.objects.create(name="Пустая категория")
    User.objects.create(name="Читатель")
    data = statistics_context(0)
    counts = sorted(c.questions_count for c in data["category_statistics"])
    assert counts == [0, 1]
    assert sorted(u.answers_count for u in data["author_statistics"]) == [0, 1]
    Answer.objects.all().delete()
    Question.objects.all().delete()
    assert statistics_context(0)["question_summary"]["total"] == 0


def test_related_search_sort_and_pagination(web):
    for i in range(12):
        Question.objects.create(text=f"Вопрос {i}", category_id=1, author_id=1)
    response = web.get("/questions/", {"related": "Pyth", "sort": "oldest"})
    assert response.context["page_obj"].paginator.count == 13
    assert response.context["page_obj"].number == 1
    assert "sort=oldest" in response.content.decode()
    response = web.get("/questions/", {"related": "нет такого автора"})
    assert response.context["total"] == 0
    assert web.get("/questions/", {"sort": "DROP TABLE"}).status_code == 400


def test_values_and_select_related_use_one_query(
        web, django_assert_num_queries):
    with django_assert_num_queries(1):
        rows = list(question_rows())
        assert rows[0]["author_name"] == "Автор"
        assert rows[0]["answers_count"] == 1
    with django_assert_num_queries(1):
        q = Question.objects.select_related("category", "author").get(pk=1)
        assert q.category.name == "Python"
        assert q.author.name == "Автор"


def test_crud_demo_leaves_no_records(web):
    before = Category.objects.count()
    output = StringIO()
    call_command("orm_demo", stdout=output)
    assert "True" in output.getvalue()
    assert Category.objects.count() == before


def test_orm_import_rolls_back_invalid_new_links(web):
    from contextlib import closing
    from django.core.management.base import CommandError

    with closing(database.get_connection()) as source, source:
        source.execute("PRAGMA foreign_keys=OFF")
        source.execute("INSERT INTO categories(id,name) VALUES(77,'Rollback')")
        source.execute(
            "INSERT INTO answers(id,text,question_id,author_id,created_on) "
            "VALUES(77,'Invalid link',999,1,'2026-09-19')")
    with pytest.raises(CommandError):
        call_command("import_legacy", source=database.DB_PATH)
    assert not Category.objects.filter(pk=77).exists()
    assert not Answer.objects.filter(pk=77).exists()
