from django.http import Http404
from django.shortcuts import get_object_or_404, render

from answers.models import Answer
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
