"""ПР10: администрирование, миграция статуса и производные значения."""

from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test.utils import CaptureQueriesContext

from categories.models import Category
from questions.models import Question


def test_admin_lists_search_filters_and_inlines(web):
    admin = get_user_model().objects.create_superuser(
        "admin_test", password="only-test-password")
    web.force_login(admin)
    for model in ["categories/category", "participants/user",
                  "questions/question", "answers/answer"]:
        assert web.get(f"/admin/{model}/").status_code == 200
    response = web.get("/admin/questions/question/", {"q": "Python"})
    assert "Как работает Python?" in response.content.decode()
    response = web.get("/admin/categories/category/1/change/")
    assert b"questions-TOTAL_FORMS" in response.content
    assert web.get("/admin/questions/question/", {
        "status__exact": "closed"}).context["cl"].result_count == 0


def test_status_managers_cancel_and_statistics(web):
    q = Question.objects.get(pk=1)
    assert Question.objects.active().for_date(q.created_on).count() == 1
    q.cancel()
    assert Question.objects.cancelled().get() == q
    assert not Question.objects.active().exists()
    response = web.get("/questions/statistics/")
    assert response.context["question_summary"]["withdrawn_count"] == 1
    assert response.context["question_summary"]["open_count"] == 0
    body = web.get("/questions/open/").content.decode()
    assert "Как работает Python?" not in body
    assert Question.objects.count() == 1


def test_slug_generated_field_and_context(web):
    category = Category.objects.get(pk=1)
    assert web.get(category.get_absolute_url()).status_code == 200
    assert web.get("/categories/topic/no-such-topic/").status_code == 404
    q = Question.objects.get(pk=1)
    q.text = "Новый текст"
    q.save()
    q.refresh_from_db()
    assert q.text_length == len(q.text)
    for url in ["/", "/questions/", "/answers/"]:
        assert web.get(url).context["active_category_count"] == 1


def test_list_query_count_does_not_grow_with_records(web):
    with CaptureQueriesContext(connection) as first:
        web.get("/questions/")
    for i in range(8):
        Question.objects.create(text=f"Дополнение {i}",
                                category_id=1, author_id=1)
    with CaptureQueriesContext(connection) as second:
        web.get("/questions/")
    assert len(first) == len(second)


def test_boolean_to_status_data_migration(transactional_db):
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    try:
        targets = [("questions", "0001_initial"),
                   ("categories", "0001_initial")]
        executor.migrate(targets)
        state = executor.loader.project_state(targets).apps
        category = state.get_model("categories", "Category").objects.create(
            name="Миграция")
        user = state.get_model("participants", "User").objects.create(
            name="Автор")
        OldQuestion = state.get_model("questions", "Question")
        ids = [OldQuestion.objects.create(text=f"Вопрос {flag}",
               category_id=category.pk, author_id=user.pk,
               is_closed=flag).pk for flag in [False, True]]
        executor = MigrationExecutor(connection)
        executor.migrate(latest)
        assert list(Question.objects.filter(pk__in=ids).order_by("pk")
                    .values_list("status", flat=True)) == ["open", "closed"]
    finally:
        MigrationExecutor(connection).migrate(latest)
