"""Списки, поиск, подробная страница и статистика через Django ORM."""

from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from questions.models import Question
from questions.forms import QuestionFilterForm, QuestionForm
from queryflow.form_views import form_response
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_http_methods
from questions.queries import (
    answer_rows, filtered_questions, question_rows, statistics_context,
)

PAGE_SIZE = 10


def list_response(request, queryset, heading, template, submitted=True):
    form = QuestionFilterForm(request.GET)
    context = {
        "heading": heading, "submitted": submitted, "cards": [], "form": form,
    }
    if not form.is_valid():
        context["error"] = "Проверьте параметры поиска, дату и номер страницы."
        return render(request, template, context, status=400)
    data = form.cleaned_data.copy()
    for key in ("category", "author"):
        data[key] = data[key].pk if data.get(key) else None
    rows = question_rows(filtered_questions(data, queryset))
    page = Paginator(rows, PAGE_SIZE).get_page(data.get("page") or 1)
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


@require_http_methods(["GET", "POST"])
def question_create(request):
    form = QuestionForm(request.POST if request.method == "POST" else None)
    return form_response(request, form, "Задать вопрос")


@require_http_methods(["GET", "POST"])
def question_edit(request, question_id):
    if question_id >= 2 ** 63:
        raise Http404
    question = get_object_or_404(Question, pk=question_id)
    form = QuestionForm(request.POST if request.method == "POST" else None,
                        instance=question)
    return form_response(request, form, "Редактировать вопрос")


@require_POST
def question_cancel(request, question_id):
    if question_id >= 2 ** 63:
        raise Http404
    question = get_object_or_404(Question, pk=question_id)
    question.cancel()
    return redirect(question)


@require_POST
def question_close(request, question_id):
    if question_id >= 2 ** 63:
        raise Http404
    question = get_object_or_404(Question, pk=question_id)
    Question.objects.filter(
        pk=question.pk, status=Question.Status.OPEN).update(
        status=Question.Status.CLOSED)
    return redirect(question)
