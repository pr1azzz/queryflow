"""Категории и связанные вопросы: представления ПР6."""

from django.shortcuts import render

from models.categories import get_category_by_id, sort_categories
from models.questions import filter_questions_by_category
from storage import load_categories, load_questions, load_users


def categories(request):
    return render(request, "categories/category_list.html", {
        "categories": sort_categories(load_categories()),
    })


def category_detail(request, category_id):
    items = load_categories()
    category = get_category_by_id(items, category_id)
    if category is None:
        return render(request, "404.html", {
            "message": "Категория не найдена",
        }, status=404)
    questions = load_questions(items, load_users())
    return render(request, "categories/category_detail.html", {
        "category": category,
        "questions": filter_questions_by_category(questions, category.id),
    })
