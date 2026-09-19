"""Функции работы с вопросами.

Содержит функции ПР1 (can_publish_question, get_question_status,
format_question_card), переработанные для работы с коллекциями.
"""

from __future__ import annotations

from datetime import date


def can_publish_question(
    text: str,
    category_active: bool,
    min_length: int = 10,
) -> bool:
    """Проверяет, можно ли опубликовать вопрос."""
    cleaned = text.strip()
    if not category_active:
        return False
    if len(cleaned) < min_length:
        return False
    return True


def get_question_status(is_closed: bool, answers_count: int) -> str:
    """Возвращает текстовый статус вопроса."""
    if is_closed:
        return "закрыт"
    if answers_count == 0:
        return "ожидает ответа"
    return "открыт"


def format_question_card(
    author: str,
    category: str,
    text: str,
    status: str,
    created_on: date,
) -> str:
    """Формирует краткую карточку вопроса для вывода."""
    preview = text.strip()
    if len(preview) > 60:
        preview = preview[:57] + "..."
    return (
        f"[{created_on.isoformat()}] {category} | {author}\n"
        f"Статус: {status}\n"
        f"Вопрос: {preview}"
    )


def add_question(
    questions: list[dict],
    text: str,
    category_id: int,
    author_id: int,
    created_on: date | None = None,
) -> dict:
    """Добавить вопрос в список questions."""
    new_id = max((item["id"] for item in questions), default=0) + 1
    question = {
        "id": new_id,
        "text": text.strip(),
        "category_id": category_id,
        "author_id": author_id,
        "is_closed": False,
        "created_on": (created_on or date.today()).isoformat(),
    }
    questions.append(question)
    return question


def find_questions(questions: list[dict], query: str) -> list[dict]:
    """Найти вопросы по подстроке текста."""
    needle = query.strip().lower()
    return [
        item for item in questions
        if needle in item["text"].lower()
    ]


def filter_questions_by_category(
    questions: list[dict],
    category_id: int,
) -> list[dict]:
    """Отобрать вопросы выбранной категории."""
    return [
        item for item in questions
        if item["category_id"] == category_id
    ]


def filter_open_questions(questions: list[dict]) -> list[dict]:
    """Отобрать незакрытые вопросы."""
    return [item for item in questions if not item["is_closed"]]


def sort_questions_by_date(
    questions: list[dict],
    reverse: bool = True,
) -> list[dict]:
    """Отсортировать вопросы по дате создания."""
    return sorted(
        questions,
        key=lambda item: item["created_on"],
        reverse=reverse,
    )


def close_question(questions: list[dict], question_id: int) -> bool:
    """Закрыть вопрос по идентификатору. Возвращает True при успехе."""
    for item in questions:
        if item["id"] == question_id:
            item["is_closed"] = True
            return True
    return False


def get_question_by_id(
    questions: list[dict],
    question_id: int,
) -> dict | None:
    """Найти вопрос по id."""
    for item in questions:
        if item["id"] == question_id:
            return item
    return None
