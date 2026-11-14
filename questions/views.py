"""Списки, поиск, подробная страница и статистика через Django ORM."""

from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from categories.models import Category
from participants.models import User
from questions.models import Question
from questions.parameters import parse_parameters
from questions.queries import (
    answer_rows, filtered_questions, question_rows, statistics_context,
)

PAGE_SIZE = 10


def list_response(request, queryset, heading, template, submitted=True):
    context = {
        "heading": heading, "submitted": submitted, "cards": [],
        "categories": Category.objects.all(), "authors": User.objects.all(),
    }
    try:
        data = parse_parameters(request.GET)
    except (ValueError, TypeError):
        context["error"] = "Проверьте параметры поиска, дату и номер страницы."
        return render(request, template, context, status=400)
    rows = question_rows(filtered_questions(data, queryset))
    page = Paginator(rows, PAGE_SIZE).get_page(data["page"])
    context.update({
        "cards": [{"question": row, "answers_count": row["answers_count"]}
                  for row in page],
        "page_obj": page, "total": page.paginator.count,
        "q": data["q"], "since": request.GET.get("since", ""),
        "category_value": str(data["category"]), "page": page.number,
        "previous_page": page.previous_page_number() if page.has_previous()
        else None,
        "next_page": page.next_page_number() if page.has_next() else None,
    })
    return render(request, template, context)


def questions(request):
    return list_response(request, Question.objects.all(), "Вопросы",
                         "questions/question_list.html")


def open_questions(request):
    return list_response(request, Question.objects.active(),
                         "Открытые вопросы", "questions/question_list.html")


def unanswered_questions(request):
    qs = Question.objects.exclude(
        status__in=[Question.Status.CLOSED, Question.Status.WITHDRAWN]
    ).filter(answers__isnull=True)
    return list_response(request, qs, "Вопросы без ответов",
                         "questions/question_list.html")


def question_detail(request, question_id):
    if question_id >= 2 ** 63:
        raise Http404("Вопрос не найден")
    question = get_object_or_404(
        Question.objects.select_related("category", "author")
        .annotate(answers_count=Count("answers")), pk=question_id)
    return render(request, "questions/question_detail.html", {
        "question": question, "answers": answer_rows(question.answers.all()),
        "answers_count": question.answers_count,
    })


def search(request):
    return list_response(request, Question.objects.all(), "Поиск вопросов",
                         "questions/search.html", bool(request.GET))


def statistics(request):
    try:
        minimum = int(request.GET.get("minimum", "0"))
        if not 0 <= minimum < 2 ** 63:
            raise ValueError
    except ValueError:
        return render(request, "questions/statistics.html", {
            "error": "Минимум должен быть неотрицательным целым числом.",
        }, status=400)
    return render(request, "questions/statistics.html",
                  statistics_context(minimum))


def withdrawn_questions(request):
    return list_response(request, Question.objects.cancelled(),
                         "Отозванные вопросы", "questions/question_list.html")
