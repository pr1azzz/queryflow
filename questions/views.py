"""Отображение объектов Question из ПР3 без Django ORM."""

from html import escape

from django.http import HttpResponse
from django.urls import reverse

from homepage.views import page
from models.answers import count_answers, get_answers_for_question
from models.questions import get_question_by_id, sort_questions_by_date
from storage import load_answers, load_categories, load_questions, load_users


def questions(request):
    """Показать список вопросов с категориями, авторами и статусами."""
    categories = load_categories()
    users = load_users()
    questions_list = load_questions(categories, users)
    answers = load_answers(questions_list, users)
    items = ""
    for question in sort_questions_by_date(questions_list):
        url = reverse("questions:detail", args=[question.id])
        total = count_answers(answers, question.id)
        status = question.status_text(total)
        badge = (
            "text-bg-secondary" if question.is_closed else "text-bg-primary"
        )
        items += f"""
        <li class="list-group-item p-4">
            <div class="d-flex flex-wrap gap-2 mb-2">
                <span class="badge {badge}">{escape(status)}</span>
                <span class="text-secondary small">
                    {escape(question.category.name)} · Ответов: {total}
                </span>
            </div>
            <h2 class="h5"><a href="{url}">{escape(question.text)}</a></h2>
            <p class="text-secondary small mb-0">
                {escape(question.author.name)} · {escape(question.created_on)}
            </p>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Вопросов пока нет.</li>'
    content = f"""
    <h1>Вопросы</h1>
    <p class="text-secondary">Обсуждения сообщества · {len(questions_list)}</p>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Вопросы", content))


def question_detail(request, question_id):
    """Найти вопрос по ID, показать связанные объекты или вернуть 404."""
    categories = load_categories()
    users = load_users()
    questions_list = load_questions(categories, users)
    question = get_question_by_id(questions_list, question_id)
    list_url = reverse("questions:list")
    if question is None:
        content = f"""
        <h1 class="text-danger">Вопрос не найден</h1>
        <p>Вопроса с таким идентификатором нет.</p>
        <a href="{list_url}" class="btn btn-outline-primary">К вопросам</a>
        """
        return HttpResponse(page("Вопрос не найден", content), status=404)

    answers = load_answers(questions_list, users)
    related = get_answers_for_question(answers, question.id)
    status = question.status_text(len(related))
    category_url = reverse("categories:detail", args=[question.category.id])
    items = ""
    for answer in related:
        answer_url = reverse("answers:detail", args=[answer.id])
        items += f"""
        <li class="list-group-item p-4">
            <p class="preserve-lines">{escape(answer.text)}</p>
            <a href="{answer_url}">Ответ №{answer.id}</a>
            <span class="text-secondary">
                · {escape(answer.author.name)} · {escape(answer.created_on)}
            </span>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Ответов пока нет.</li>'
    content = f"""
    <a href="{list_url}">← Все вопросы</a>
    <article class="card my-4"><div class="card-body p-4">
        <p class="text-secondary">Вопрос №{question.id}</p>
        <h1 class="h2 preserve-lines">{escape(question.text)}</h1>
        <p>Категория: <a href="{category_url}">
            {escape(question.category.name)}</a></p>
        <p>Автор: {escape(question.author.name)}</p>
        <p>Дата: {escape(question.created_on)}</p>
        <p class="mb-0">Статус:
            <span class="badge text-bg-primary">{escape(status)}</span>
        </p>
    </div></article>
    <h2 class="h4">Ответы · {len(related)}</h2>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page(f"Вопрос №{question.id}", content))
