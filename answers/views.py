"""Ответы и связанные объекты передаются в шаблоны ПР6."""

from django.shortcuts import render

from models.answers import get_answer_by_id
from storage import load_answers, load_categories, load_questions, load_users


def answers(request):
    users = load_users()
    questions = load_questions(load_categories(), users)
    return render(request, "answers/answer_list.html", {
        "answers": load_answers(questions, users),
    })


def answer_detail(request, answer_id):
    users = load_users()
    questions = load_questions(load_categories(), users)
    answer = get_answer_by_id(load_answers(questions, users), answer_id)
    if answer is None:
        return render(request, "404.html", {
            "message": "Ответ не найден",
        }, status=404)
    return render(request, "answers/answer_detail.html", {"answer": answer})
