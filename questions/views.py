"""Объекты ПР3 передаются в шаблоны через контекст."""

from django.shortcuts import render

from models.answers import count_answers, get_answers_for_question
from models.questions import get_question_by_id, sort_questions_by_date
from storage import load_answers, load_categories, load_questions, load_users


def questions(request):
    users = load_users()
    items = load_questions(load_categories(), users)
    answers = load_answers(items, users)
    cards = [
        {"question": item, "answers_count": count_answers(answers, item.id)}
        for item in sort_questions_by_date(items)
    ]
    return render(request, "questions/question_list.html", {"cards": cards})


def question_detail(request, question_id):
    users = load_users()
    items = load_questions(load_categories(), users)
    question = get_question_by_id(items, question_id)
    if question is None:
        return render(request, "404.html", {
            "message": "Вопрос не найден",
        }, status=404)
    answers = get_answers_for_question(load_answers(items, users), question.id)
    return render(request, "questions/question_detail.html", {
        "question": question, "answers": answers,
        "answers_count": len(answers),
    })
