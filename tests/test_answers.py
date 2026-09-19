"""Тесты функций ответов."""

from answers import add_answer, count_answers, get_answers_for_question


def test_add_answer() -> None:
    answers: list[dict] = []
    item = add_answer(answers, 1, "Это изолированная среда.", 2)
    assert item["id"] == 1
    assert len(answers) == 1


def test_count_answers() -> None:
    answers: list[dict] = []
    add_answer(answers, 1, "Первый ответ", 1)
    add_answer(answers, 1, "Второй ответ", 2)
    add_answer(answers, 2, "Другой вопрос", 1)
    assert count_answers(answers, 1) == 2
    assert count_answers(answers, 2) == 1


def test_get_answers_for_question() -> None:
    answers: list[dict] = []
    add_answer(answers, 5, "Ответ A", 1)
    add_answer(answers, 7, "Ответ B", 1)
    items = get_answers_for_question(answers, 5)
    assert len(items) == 1
    assert items[0]["text"] == "Ответ A"
