"""Ответы с сохранением связей Answer → Question и User из ПР3."""

from html import escape

from django.http import HttpResponse
from django.urls import reverse

from homepage.views import page
from models.answers import get_answer_by_id
from storage import load_answers, load_categories, load_questions, load_users


def answers(request):
    categories = load_categories()
    users = load_users()
    questions = load_questions(categories, users)
    answers_list = load_answers(questions, users)
    items = ""
    for answer in answers_list:
        url = reverse("answers:detail", args=[answer.id])
        question_url = reverse("questions:detail", args=[answer.question.id])
        items += f"""
        <li class="list-group-item p-4">
            <h2 class="h5"><a href="{url}">Ответ №{answer.id}</a></h2>
            <p class="preserve-lines">{escape(answer.text)}</p>
            <p>К вопросу: <a href="{question_url}">
                {escape(answer.question.text)}</a></p>
            <p class="text-secondary small mb-0">
                {escape(answer.author.name)} · {escape(answer.created_on)}
            </p>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Ответов пока нет.</li>'
    content = f"""
    <h1>Ответы</h1>
    <p class="text-secondary">Объяснения участников · {len(answers_list)}</p>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Ответы", content))


def answer_detail(request, answer_id):
    categories = load_categories()
    users = load_users()
    questions = load_questions(categories, users)
    answers_list = load_answers(questions, users)
    answer = get_answer_by_id(answers_list, answer_id)
    list_url = reverse("answers:list")
    if answer is None:
        content = f"""
        <h1 class="text-danger">Ответ не найден</h1>
        <a href="{list_url}" class="btn btn-outline-primary">К ответам</a>
        """
        return HttpResponse(page("Ответ не найден", content), status=404)
    question_url = reverse("questions:detail", args=[answer.question.id])
    content = f"""
    <a href="{list_url}">← Все ответы</a>
    <article class="card mt-4"><div class="card-body p-4">
        <h1 class="h2">Ответ №{answer.id}</h1>
        <p class="lead preserve-lines">{escape(answer.text)}</p>
        <p>Автор: {escape(answer.author.name)}</p>
        <p>Дата: {escape(answer.created_on)}</p>
        <p>К вопросу: <a href="{question_url}">
            {escape(answer.question.text)}</a></p>
        <p class="text-secondary mb-0">
            Категория: {escape(answer.question.category.name)}
        </p>
    </div></article>
    """
    return HttpResponse(page(f"Ответ №{answer.id}", content))
