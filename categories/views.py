from django.http import Http404
from django.shortcuts import get_object_or_404, render

from categories.models import Category
from questions.queries import question_rows


def categories(request):
    return render(request, "categories/category_list.html", {
        "categories": Category.objects.all(), "heading": "Категории",
    })


def active_categories(request):
    return render(request, "categories/category_list.html", {
        "categories": Category.objects.filter(is_active=True),
        "heading": "Активные категории",
    })


def category_detail(request, category_id=None, slug=None):
    if category_id is not None and category_id >= 2 ** 63:
        raise Http404("Категория не найдена")
    lookup = {"slug": slug} if slug else {"pk": category_id}
    category = get_object_or_404(Category, **lookup)
    return render(request, "categories/category_detail.html", {
        "category": category, "questions": question_rows(
            category.questions.all()),
    })
