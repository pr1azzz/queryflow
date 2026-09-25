"""Тесты вопросов (объектная модель ПР3, сценарии ПР1)."""

from datetime import date

from models import Category, Question, User
from models.questions import (
    add_question,
    can_publish_question,
    close_question,
    find_questions,
    get_question_status,
)


def _sample_category(active: bool = True) -> Category:
    return Category(1, "Python", active)


def _sample_user() -> User:
    return User(1, "Иван Петров", "user")


def test_question_creation() -> None:
    category = _sample_category()
    author = _sample_user()
    question = Question(
        1,
        "Как работает venv в Python?",
        category,
        author,
        created_on=date(2026, 9, 19),
    )
    assert question.id == 1
    assert question.category is category
    assert question.author is author
    assert question.created_on == "2026-09-19"
    assert not question.is_closed
    assert "venv" in str(question)


def test_question_close() -> None:
    question = Question(
        1,
        "Как работает venv в Python?",
        _sample_category(),
        _sample_user(),
    )
    question.close()
    assert question.is_closed


def test_can_publish_question() -> None:
    assert can_publish_question("Достаточно длинный текст", True)
    assert not can_publish_question("коротко", True)
    assert not can_publish_question("Достаточно длинный текст", False)


def test_get_question_status() -> None:
    assert get_question_status(True, 5) == "закрыт"
    assert get_question_status(False, 0) == "ожидает ответа"
    assert get_question_status(False, 2) == "открыт"


def test_add_question() -> None:
    questions: list[Question] = []
    item = add_question(
        questions,
        "Как работает venv в Python?",
        _sample_category(),
        _sample_user(),
        created_on=date(2026, 9, 19),
    )
    assert item is not None
    assert len(questions) == 1
    assert item.id == 1
    assert item.created_on == "2026-09-19"
    assert item.category.name == "Python"


def test_add_question_inactive_category() -> None:
    questions: list[Question] = []
    result = add_question(
        questions,
        "Как работает venv в Python?",
        _sample_category(active=False),
        _sample_user(),
    )
    assert result is None
    assert len(questions) == 0


def test_find_questions() -> None:
    questions: list[Question] = []
    cat = _sample_category()
    user = _sample_user()
    add_question(questions, "Как работает venv?", cat, user)
    add_question(
        questions,
        "Что такое ORM?",
        Category(2, "Django", True),
        user,
    )
    found = find_questions(questions, "venv")
    assert len(found) == 1


def test_close_question_function() -> None:
    questions: list[Question] = []
    add_question(
        questions,
        "Как работает venv в Python?",
        _sample_category(),
        _sample_user(),
    )
    assert close_question(questions, 1)
    assert questions[0].is_closed
