"""Категории и их вопросы из SQLite."""

from django.shortcuts import render

from db.queries import fetch_all, fetch_one


def categories(request):
    return render(request, "categories/category_list.html", {
        "categories": fetch_all("category_list"), "heading": "Категории",
    })


def active_categories(request):
    return render(request, "categories/category_list.html", {
        "categories": fetch_all("active_categories"),
        "heading": "Активные категории",
    })


def category_detail(request, category_id):
    category = (fetch_one("category_detail", (category_id,))
                if category_id < 2 ** 63 else None)
    if category is None:
        return render(request, "404.html", {
            "message": "Категория не найдена",
        }, status=404)
    return render(request, "categories/category_detail.html", {
        "category": category,
        "questions": fetch_all("category_questions", (category_id,)),
    })
