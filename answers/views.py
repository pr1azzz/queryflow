from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render

from answers.forms import AnswerForm
from answers.models import Answer
from questions.models import Question
from queryflow.form_views import form_response
from questions.queries import answer_rows


def answers(request):
    return render(request, "answers/answer_list.html", {
        "answers": answer_rows(),
    })


def answer_detail(request, answer_id):
    if answer_id >= 2 ** 63:
        raise Http404("Ответ не найден")
    answer = get_object_or_404(Answer.objects.select_related(
        "question__category", "author"), pk=answer_id)
    return render(request, "answers/answer_detail.html", {"answer": answer})


@require_http_methods(["GET", "POST"])
def answer_create(request, question_id):
    if question_id >= 2 ** 63:
        raise Http404
    question = get_object_or_404(Question, pk=question_id)
    form = AnswerForm(request.POST if request.method == "POST" else None,
                      question=question)
    return form_response(request, form, f"Ответить на вопрос №{question.pk}")


@require_http_methods(["GET", "POST"])
def answer_edit(request, answer_id):
    if answer_id >= 2 ** 63:
        raise Http404
    answer = get_object_or_404(Answer.objects.select_related("question"),
                               pk=answer_id)
    form = AnswerForm(request.POST if request.method == "POST" else None,
                      instance=answer, question=answer.question)
    return form_response(request, form, "Редактировать ответ")
