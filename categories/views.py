"""Категории и относящиеся к ним вопросы из JSON-хранилища."""

from html import escape

from django.http import HttpResponse
from django.urls import reverse

from homepage.views import page
from models.categories import get_category_by_id, sort_categories
from models.questions import filter_questions_by_category
from storage import load_categories, load_questions, load_users


def categories(request):
    items = ""
    for category in sort_categories(load_categories()):
        url = reverse("categories:detail", args=[category.id])
        status = "Активна" if category.is_available() else "Архив"
        items += f"""
        <li class="list-group-item p-3 d-flex flex-wrap gap-3">
            <a href="{url}" class="me-auto">{escape(category.name)}</a>
            <span class="badge text-bg-light">{status}</span>
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Категорий пока нет.</li>'
    content = f"""
    <h1>Категории</h1>
    <p class="text-secondary">Выберите тему, чтобы увидеть её вопросы.</p>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Категории", content))


def category_detail(request, category_id):
    categories_list = load_categories()
    category = get_category_by_id(categories_list, category_id)
    list_url = reverse("categories:list")
    if category is None:
        content = f"""
        <h1 class="text-danger">Категория не найдена</h1>
        <a href="{list_url}" class="btn btn-outline-primary">К категориям</a>
        """
        return HttpResponse(page("Категория не найдена", content), status=404)
    questions = load_questions(categories_list, load_users())
    related = filter_questions_by_category(questions, category.id)
    items = ""
    for question in related:
        url = reverse("questions:detail", args=[question.id])
        items += (
            f'<li class="list-group-item p-3"><a href="{url}">'
            f'{escape(question.text)}</a></li>'
        )
    if not items:
        items = (
            '<li class="list-group-item">В этой теме пока нет вопросов.</li>'
        )
    status = "Доступна для публикации" if category.is_available() else "Архив"
    content = f"""
    <a href="{list_url}">← Все категории</a>
    <h1 class="mt-4">{escape(category.name)}</h1>
    <p class="text-secondary">Категория №{category.id} · {status}</p>
    <h2 class="h4">Вопросы · {len(related)}</h2>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page(category.name, content))
