"""Сохранение и загрузка данных QueryFlow в JSON (объектная модель ПР3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.answers import Answer
from models.categories import Category, get_category_by_id
from models.questions import Question, get_question_by_id
from models.users import User, get_user_by_id

DATA_DIR = Path(__file__).resolve().parent / "data"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filename: str, default: Any) -> Any:
    """Загрузить данные из JSON-файла.

    При отсутствии файла или некорректном JSON возвращает default.
    """
    path = DATA_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"Предупреждение: файл {filename} повреждён, "
              f"используются пустые данные.")
        return default


def save_json(filename: str, data: Any) -> None:
    """Сохранить данные в JSON-файл."""
    _ensure_data_dir()
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_categories() -> list[Category]:
    """Загрузить категории как коллекцию объектов Category."""
    raw = load_json("categories.json", [])
    return [
        Category(
            category_id=int(item["id"]),
            name=str(item["name"]),
            is_active=bool(item.get("is_active", True)),
        )
        for item in raw
    ]


def save_categories(categories: list[Category]) -> None:
    """Сохранить объекты Category в JSON."""
    items = [
        {
            "id": category.id,
            "name": category.name,
            "is_active": category.is_active,
        }
        for category in sorted(categories, key=lambda item: item.id)
    ]
    save_json("categories.json", items)


def load_users() -> list[User]:
    """Загрузить пользователей как коллекцию объектов User."""
    raw = load_json("users.json", [])
    return [User.from_data(item) for item in raw]


def save_users(users: list[User]) -> None:
    """Сохранить объекты User в JSON."""
    items = [
        {
            "id": user.id,
            "name": user.name,
            "role": user.role,
        }
        for user in sorted(users, key=lambda item: item.id)
    ]
    save_json("users.json", items)


def load_questions(
    categories: list[Category],
    users: list[User],
) -> list[Question]:
    """Загрузить вопросы, восстановив связи с Category и User."""
    raw = load_json("questions.json", [])
    questions: list[Question] = []
    for item in raw:
        category = get_category_by_id(categories, int(item["category_id"]))
        author = get_user_by_id(users, int(item["author_id"]))
        if category is None or author is None:
            continue
        question = Question(
            question_id=int(item["id"]),
            text=str(item["text"]),
            category=category,
            author=author,
            created_on=str(item.get("created_on", "")),
            is_closed=bool(item.get("is_closed", False)),
        )
        questions.append(question)
    return questions


def save_questions(questions: list[Question]) -> None:
    """Сохранить объекты Question: связи → category_id / author_id."""
    items = [
        {
            "id": question.id,
            "text": question.text,
            "category_id": question.category.id,
            "author_id": question.author.id,
            "is_closed": question.is_closed,
            "created_on": question.created_on,
        }
        for question in questions
    ]
    save_json("questions.json", items)


def load_answers(
    questions: list[Question],
    users: list[User],
) -> list[Answer]:
    """Загрузить ответы, восстановив связи с Question и User."""
    raw = load_json("answers.json", [])
    answers: list[Answer] = []
    for item in raw:
        question = get_question_by_id(questions, int(item["question_id"]))
        author = get_user_by_id(users, int(item["author_id"]))
        if question is None or author is None:
            continue
        answer = Answer(
            answer_id=int(item["id"]),
            text=str(item["text"]),
            question=question,
            author=author,
            created_on=str(item.get("created_on", "")),
        )
        answers.append(answer)
    return answers


def save_answers(answers: list[Answer]) -> None:
    """Сохранить объекты Answer: связи → question_id / author_id."""
    items = [
        {
            "id": answer.id,
            "question_id": answer.question.id,
            "text": answer.text,
            "author_id": answer.author.id,
            "created_on": answer.created_on,
        }
        for answer in answers
    ]
    save_json("answers.json", items)
