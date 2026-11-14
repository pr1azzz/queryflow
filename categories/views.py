from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render

from categories.forms import CategoryForm
from categories.models import Category
from queryflow.form_views import form_response
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


@staff_member_required
@require_http_methods(["GET", "POST"])
def category_edit(request, category_id):
    if category_id >= 2 ** 63:
        raise Http404
    category = get_object_or_404(Category, pk=category_id)
    form = CategoryForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None, instance=category)
    return form_response(request, form, "Редактировать категорию")
