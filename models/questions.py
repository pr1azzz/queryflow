"""Класс Question и функции работы с коллекцией вопросов.

Содержит функции ПР1 (can_publish_question, get_question_status,
format_question_card), адаптированные к объектной модели ПР3.
"""

from __future__ import annotations

from datetime import date

from .categories import Category
from .users import User


class Question:
    """Вопрос пользователя в выбранной категории."""

    def __init__(
        self,
        question_id: int,
        text: str,
        category: Category,
        author: User,
        created_on: date | str | None = None,
        is_closed: bool = False,
    ) -> None:
        """Создать объект вопроса.

        Хранит ссылки на объекты Category и User, а не только их id.
        """
        self.id = question_id
        self.text = text.strip()
        self.category = category
        self.author = author
        self.is_closed = is_closed
        if created_on is None:
            self.created_on = date.today().isoformat()
        elif isinstance(created_on, date):
            self.created_on = created_on.isoformat()
        else:
            self.created_on = str(created_on)

    def close(self) -> None:
        """Закрыть вопрос (изменить состояние объекта)."""
        self.is_closed = True

    def status_text(self, answers_count: int) -> str:
        """Вернуть текстовый статус с учётом числа ответов."""
        return get_question_status(self.is_closed, answers_count)

    def __str__(self) -> str:
        """Вернуть строковое представление вопроса."""
        state = "закрыт" if self.is_closed else "открыт"
        preview = self.text
        if len(preview) > 50:
            preview = preview[:47] + "..."
        return (
            f"[{self.created_on}] {self.category.name} | "
            f"{self.author.name}: {preview} ({state})"
        )


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
    questions: list[Question],
    text: str,
    category: Category,
    author: User,
    created_on: date | None = None,
) -> Question | None:
    """Создать объект Question и добавить его в коллекцию.

    Возвращает None, если публикация невозможна (неактивная категория
    или слишком короткий текст).
    """
    if not can_publish_question(text, category.is_available()):
        return None
    new_id = max((item.id for item in questions), default=0) + 1
    question = Question(
        question_id=new_id,
        text=text,
        category=category,
        author=author,
        created_on=created_on,
    )
    questions.append(question)
    return question


def find_questions(
    questions: list[Question],
    query: str,
) -> list[Question]:
    """Найти вопросы по подстроке текста."""
    needle = query.strip().lower()
    return [item for item in questions if needle in item.text.lower()]


def filter_questions_by_category(
    questions: list[Question],
    category_id: int,
) -> list[Question]:
    """Отобрать вопросы выбранной категории."""
    return [
        item for item in questions
        if item.category.id == category_id
    ]


def filter_open_questions(questions: list[Question]) -> list[Question]:
    """Отобрать незакрытые вопросы."""
    return [item for item in questions if not item.is_closed]


def sort_questions_by_date(
    questions: list[Question],
    reverse: bool = True,
) -> list[Question]:
    """Отсортировать вопросы по дате создания."""
    return sorted(
        questions,
        key=lambda item: item.created_on,
        reverse=reverse,
    )


def close_question(questions: list[Question], question_id: int) -> bool:
    """Найти вопрос и вызвать метод close(). Возвращает True при успехе."""
    question = get_question_by_id(questions, question_id)
    if question is None:
        return False
    question.close()
    return True


def get_question_by_id(
    questions: list[Question],
    question_id: int,
) -> Question | None:
    """Найти вопрос по id."""
    for item in questions:
        if item.id == question_id:
            return item
    return None
