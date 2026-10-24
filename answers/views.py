"""ПР7: JOIN связывает ответ с вопросом, категорией и автором."""

from django.shortcuts import render

from db.queries import fetch_all, fetch_one


def answers(request):
    return render(request, "answers/answer_list.html", {
        "answers": fetch_all("answer_list"),
    })


def answer_detail(request, answer_id):
    answer = (fetch_one("answer_detail", (answer_id,))
              if answer_id < 2 ** 63 else None)
    if answer is None:
        return render(request, "404.html", {
            "message": "Ответ не найден",
        }, status=404)
    return render(request, "answers/answer_detail.html", {"answer": answer})
