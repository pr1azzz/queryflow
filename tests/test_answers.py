"""Тесты ответов (объектная модель ПР3)."""

from models import Answer, Category, Question, User
from models.answers import add_answer, count_answers, get_answers_for_question


def _sample_question(closed: bool = False) -> Question:
    category = Category(1, "Python", True)
    author = User(1, "Иван Петров", "user")
    question = Question(
        1,
        "Как работает venv в Python?",
        category,
        author,
    )
    if closed:
        question.close()
    return question


def test_answer_creation() -> None:
    question = _sample_question()
    author = User(2, "Анна Смирнова", "moderator")
    answer = Answer(1, "Это изолированная среда.", question, author)
    assert answer.id == 1
    assert answer.question is question
    assert answer.author is author
    assert "Анна" in str(answer)


def test_add_answer() -> None:
    answers: list[Answer] = []
    question = _sample_question()
    author = User(2, "Анна", "user")
    item = add_answer(answers, question, "Это изолированная среда.", author)
    assert item is not None
    assert item.id == 1
    assert len(answers) == 1
    assert item.question.id == 1


def test_add_answer_to_closed_question() -> None:
    answers: list[Answer] = []
    result = add_answer(
        answers,
        _sample_question(closed=True),
        "Поздно",
        User(2, "Анна", "user"),
    )
    assert result is None
    assert len(answers) == 0


def test_count_answers() -> None:
    answers: list[Answer] = []
    q1 = _sample_question()
    q2 = Question(
        2,
        "Что такое ORM?",
        Category(2, "Django", True),
        User(1, "Иван", "user"),
    )
    author = User(2, "Анна", "user")
    add_answer(answers, q1, "Первый ответ", author)
    add_answer(answers, q1, "Второй ответ", author)
    add_answer(answers, q2, "Другой вопрос", author)
    assert count_answers(answers, 1) == 2
    assert count_answers(answers, 2) == 1


def test_get_answers_for_question() -> None:
    answers: list[Answer] = []
    q5 = Question(
        5,
        "Вопрос пять",
        Category(1, "Python", True),
        User(1, "Иван", "user"),
    )
    q7 = Question(
        7,
        "Вопрос семь",
        Category(1, "Python", True),
        User(1, "Иван", "user"),
    )
    author = User(1, "Иван", "user")
    add_answer(answers, q5, "Ответ A", author)
    add_answer(answers, q7, "Ответ B", author)
    items = get_answers_for_question(answers, 5)
    assert len(items) == 1
    assert items[0].text == "Ответ A"
