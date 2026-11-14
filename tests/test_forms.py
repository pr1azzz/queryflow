"""ПР11: реальные HTTP-сценарии форм, ошибки, CSRF, изображения."""

from datetime import timedelta
from io import BytesIO

import pytest
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError, IntegrityError, transaction
from django.test import Client
from django.utils import timezone

from answers.models import Answer
from categories.models import Category
from questions.forms import QuestionForm
from questions.models import Question


def question_data(**changes):
    data = {"text": "Как проверить форму Django?", "category": 1,
            "author": 1, "created_on": timezone.localdate().isoformat()}
    data.update(changes)
    return data


def image_file(name="example.png"):
    buffer = BytesIO()
    Image.new("RGB", (16, 16), "blue").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(),
                              content_type="image/png")


def test_create_redirect_edit_and_refresh_do_not_duplicate(web):
    count = Question.objects.count()
    assert web.get("/questions/create/").status_code == 200
    assert Question.objects.count() == count
    response = web.post("/questions/create/", question_data())
    assert response.status_code == 302
    q = Question.objects.get(text=question_data()["text"])
    assert response.url == q.get_absolute_url()
    assert web.get(response.url).status_code == 200
    assert web.get(response.url).status_code == 200
    assert Question.objects.count() == count + 1
    response = web.post(f"/questions/{q.pk}/edit/", question_data())
    assert response.status_code == 302
    assert Question.objects.count() == count + 1
    q.refresh_from_db()
    assert q.text == question_data()["text"]


@pytest.mark.parametrize("data, field", [
    (question_data(text=" "), "text"),
    (question_data(text="мало"), "text"),
    (question_data(category=999), "category"),
    (question_data(created_on="broken"), "created_on"),
    (question_data(created_on=(timezone.localdate() + timedelta(days=1))
                   .isoformat()), "created_on"),
])
def test_invalid_question_keeps_values_and_does_not_save(web, data, field):
    count = Question.objects.count()
    response = web.post("/questions/create/", data)
    assert response.status_code == 400
    assert field in response.context["form"].errors
    assert response.context["form"].is_bound
    assert Question.objects.count() == count


def test_duplicate_create_edit_conflict_and_withdrawal(web):
    data = question_data()
    assert web.post("/questions/create/", data).status_code == 302
    first = Question.objects.get(text=data["text"])
    assert web.post("/questions/create/", data).status_code == 400
    second = Question.objects.create(text="Другой тестовый вопрос",
                                     category_id=1, author_id=1)
    assert web.post(f"/questions/{second.pk}/edit/", data).status_code == 400
    second.refresh_from_db()
    assert second.text == "Другой тестовый вопрос"
    assert web.get(f"/questions/{first.pk}/cancel/").status_code == 405
    first.refresh_from_db()
    assert first.status == Question.Status.OPEN
    assert web.post(f"/questions/{first.pk}/cancel/").status_code == 302
    first.refresh_from_db()
    assert first.status == Question.Status.WITHDRAWN
    assert web.post("/questions/create/", data).status_code == 302
    assert Question.objects.filter(text=data["text"]).count() == 2


def test_duplicate_constraint_catches_non_form_writes(web):
    q = Question.objects.get(pk=1)
    with pytest.raises(IntegrityError), transaction.atomic():
        Question.objects.create(text=q.text, author=q.author,
                                category=q.category)


def test_answer_create_edit_and_closed_question(web):
    data = {"text": "Используйте Django Test Client.", "author": 1,
            "created_on": timezone.localdate().isoformat()}
    response = web.post("/answers/for/1/create/", data)
    assert response.status_code == 302
    answer = Answer.objects.get(text=data["text"])
    assert answer.question_id == 1
    data["text"] = "Обновлённый ответ для проверки."
    assert web.post(f"/answers/{answer.pk}/edit/", data).status_code == 302
    answer.refresh_from_db()
    assert answer.text == data["text"]
    assert web.get("/questions/1/close/").status_code == 405
    assert web.post("/questions/1/close/").status_code == 302
    count = Answer.objects.count()
    assert web.post("/answers/for/1/create/", data).status_code == 400
    assert web.post(f"/answers/{answer.pk}/edit/", data).status_code == 400
    assert Answer.objects.count() == count


def test_cross_field_dates_and_archived_category(web):
    data = {"text": "Тестовый ответ", "author": 1, "created_on": "2020-01-01"}
    response = web.post("/answers/for/1/create/", data)
    assert response.status_code == 400
    assert "created_on" in response.context["form"].errors
    original = Question.objects.get(pk=1)
    response = web.post(
        "/questions/1/edit/",
        question_data(
            text=original.text))
    assert response.status_code == 400  # already has an earlier answer
    Category.objects.filter(pk=1).update(is_active=False)
    assert web.post("/questions/create/", question_data()).status_code == 400


def test_csrf_required_for_every_mutation(web):
    client = Client(enforce_csrf_checks=True)
    for url in ["/questions/create/", "/questions/1/edit/",
                "/questions/1/cancel/", "/questions/1/close/",
                "/answers/for/1/create/", "/answers/1/edit/"]:
        assert client.post(url, question_data()).status_code == 403
    client.get("/questions/create/")
    token = client.cookies["csrftoken"].value
    response = client.post("/questions/create/", {
        **question_data(), "csrfmiddlewaretoken": token})
    assert response.status_code == 302


@pytest.mark.parametrize("url", ["/questions/999/edit/",
                                 "/answers/999/edit/",
                                 "/answers/for/999/create/"])
def test_form_missing_objects_are_404(web, url):
    assert web.get(url).status_code == 404


@pytest.mark.parametrize("error, expected", [(IntegrityError, 400),
                                             (DatabaseError, 503)])
def test_database_failure_returns_form_without_losing_input(
        web, monkeypatch, error, expected):
    def fail(*args, **kwargs):
        raise error("test failure")
    monkeypatch.setattr(QuestionForm, "save", fail)
    count = Question.objects.count()
    response = web.post("/questions/create/", question_data())
    assert response.status_code == expected
    assert response.context["form"].non_field_errors()
    assert response.context["form"]["text"].value() == question_data()["text"]
    assert Question.objects.count() == count


def test_image_upload_replace_clear_and_invalid_file(web, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"
    assert web.get("/categories/1/edit/").status_code == 302
    admin = get_user_model().objects.create_superuser(
        "image_admin", password="test-only-password")
    web.force_login(admin)
    for name in ["first.png", "second.png"]:
        response = web.post("/categories/1/edit/", {
            "name": "Python", "is_active": "on", "image": image_file(name)})
        assert response.status_code == 302
        category = Category.objects.get(pk=1)
        assert category.image.storage.exists(category.image.name)
        assert category.image.url in web.get(
            category.get_absolute_url()).content.decode()
    response = web.post("/categories/1/edit/", {
        "name": "Python",
        "image": SimpleUploadedFile("bad.png", b"not image")})
    assert response.status_code == 400
    assert "image" in response.context["form"].errors
    assert web.post("/categories/1/edit/", {
        "name": "Python", "image-clear": "on"}).status_code == 302
    assert not Category.objects.get(pk=1).image


def test_admin_image_widget_and_upload(web, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "admin-media"
    admin = get_user_model().objects.create_superuser(
        "upload_admin", password="test-only-password")
    web.force_login(admin)
    response = web.post("/admin/categories/category/add/", {
        "name": "Картинки", "slug": "pictures", "is_active": "on",
        "image": image_file(), "questions-TOTAL_FORMS": "0",
        "questions-INITIAL_FORMS": "0", "questions-MIN_NUM_FORMS": "0",
        "questions-MAX_NUM_FORMS": "1000", "_save": "Сохранить"})
    assert response.status_code == 302
    category = Category.objects.get(slug="pictures")
    assert category.image.storage.exists(category.image.name)
    assert category.image.url in web.get(
        category.get_absolute_url()).content.decode()
