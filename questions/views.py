"""ПР7: SQL-выборки, поиск и статистика без Django ORM."""

from datetime import date

from django.shortcuts import render

from db.queries import fetch_all, fetch_one

PAGE_SIZE = 10


def _cards(rows):
    return [{"question": row, "answers_count": row["answers_count"]}
            for row in rows]


def questions(request):
    return render(request, "questions/question_list.html", {
        "cards": _cards(fetch_all("question_list")), "heading": "Вопросы",
    })


def open_questions(request):
    return render(request, "questions/question_list.html", {
        "cards": _cards(fetch_all("open_questions")),
        "heading": "Открытые вопросы",
    })


def unanswered_questions(request):
    return render(request, "questions/question_list.html", {
        "cards": _cards(fetch_all("unanswered_questions")),
        "heading": "Вопросы без ответов",
    })


def question_detail(request, question_id):
    question = (fetch_one("question_detail", (question_id,))
                if question_id < 2 ** 63 else None)
    if question is None:
        return render(request, "404.html", {
            "message": "Вопрос не найден",
        }, status=404)
    return render(request, "questions/question_detail.html", {
        "question": question,
        "answers": fetch_all("question_answers", (question_id,)),
        "answers_count": question["answers_count"],
    })


def search(request):
    """Проверить GET-параметры и передать значения отдельно от текста SQL."""
    text = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    since = request.GET.get("since", "")
    context = {
        "q": text, "category_value": category, "since": since,
        "categories": fetch_all("category_list"), "cards": [],
        "submitted": bool(request.GET), "total": 0,
    }
    try:
        page = int(request.GET.get("page", "1"))
        if not 1 <= page <= 1000000:
            raise ValueError("Номер страницы должен быть от 1 до 1000000.")
        category_id = int(category) if category else None
        if category_id is not None and not 1 <= category_id < 2 ** 63:
            raise ValueError("Укажите положительный ID категории.")
        if len(text) > 200:
            raise ValueError("Поисковый текст длиннее 200 знаков.")
        if since and date.fromisoformat(since).isoformat() != since:
            raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД.")
    except ValueError:
        context["error"] = (
            "Проверьте параметры: текст до 200 знаков, положительный ID "
            "категории, дата ГГГГ-ММ-ДД, номер страницы от 1 до 1000000."
        )
        return render(request, "questions/search.html", context, status=400)
    if context["submitted"]:
        parameters = (text, text, category_id, category_id, since, since)
        context["total"] = fetch_one("search_count", parameters)["total"]
        rows = fetch_all("question_search", (
            *parameters, PAGE_SIZE, (page - 1) * PAGE_SIZE,
        ))
        context.update({
            "cards": _cards(rows), "page": page,
            "previous_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page * PAGE_SIZE < context["total"]
            else None,
        })
    return render(request, "questions/search.html", context)


def statistics(request):
    """Отобразить два агрегатных и два группирующих запроса."""
    try:
        minimum = int(request.GET.get("minimum", "0"))
        if not 0 <= minimum < 2 ** 63:
            raise ValueError
    except ValueError:
        return render(request, "questions/statistics.html", {
            "error": "Минимум должен быть неотрицательным целым числом.",
        }, status=400)
    return render(request, "questions/statistics.html", {
        "question_summary": fetch_one("question_summary"),
        "answer_summary": fetch_one("answer_summary"),
        "category_statistics": fetch_all("category_statistics", (minimum,)),
        "author_statistics": fetch_all("author_statistics"),
        "users": fetch_all("user_list"), "minimum": minimum,
    })
