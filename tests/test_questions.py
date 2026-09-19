"""Тесты функций вопросов (включая сценарии ПР1)."""

from datetime import date

from questions import (
    add_question,
    can_publish_question,
    find_questions,
    get_question_status,
)


def test_can_publish_question() -> None:
    assert can_publish_question("Достаточно длинный текст", True)
    assert not can_publish_question("коротко", True)
    assert not can_publish_question("Достаточно длинный текст", False)


def test_get_question_status() -> None:
    assert get_question_status(True, 5) == "закрыт"
    assert get_question_status(False, 0) == "ожидает ответа"
    assert get_question_status(False, 2) == "открыт"


def test_add_question() -> None:
    questions: list[dict] = []
    item = add_question(
        questions,
        "Как работает venv в Python?",
        category_id=1,
        author_id=1,
        created_on=date(2026, 9, 19),
    )
    assert len(questions) == 1
    assert item["id"] == 1
    assert item["created_on"] == "2026-09-19"


def test_find_questions() -> None:
    questions: list[dict] = []
    add_question(questions, "Как работает venv?", 1, 1)
    add_question(questions, "Что такое ORM?", 2, 1)
    found = find_questions(questions, "venv")
    assert len(found) == 1
