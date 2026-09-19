"""Функции работы с ответами на вопросы."""

from __future__ import annotations

from datetime import date


def add_answer(
    answers: list[dict],
    question_id: int,
    text: str,
    author_id: int,
    created_on: date | None = None,
) -> dict:
    """Добавить ответ к вопросу."""
    new_id = max((item["id"] for item in answers), default=0) + 1
    answer = {
        "id": new_id,
        "question_id": question_id,
        "text": text.strip(),
        "author_id": author_id,
        "created_on": (created_on or date.today()).isoformat(),
    }
    answers.append(answer)
    return answer


def get_answers_for_question(
    answers: list[dict],
    question_id: int,
) -> list[dict]:
    """Вернуть ответы для указанного вопроса."""
    return [
        item for item in answers
        if item["question_id"] == question_id
    ]


def count_answers(answers: list[dict], question_id: int) -> int:
    """Подсчитать число ответов на вопрос."""
    return len(get_answers_for_question(answers, question_id))


def remove_answer(answers: list[dict], answer_id: int) -> bool:
    """Удалить ответ по идентификатору."""
    for index, item in enumerate(answers):
        if item["id"] == answer_id:
            del answers[index]
            return True
    return False
