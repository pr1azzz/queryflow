"""Сохранение и загрузка данных QueryFlow в JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def load_categories() -> dict[int, dict]:
    """Загрузить категории: ключ — id, значение — словарь данных."""
    raw = load_json("categories.json", [])
    return {int(item["id"]): item for item in raw}


def save_categories(categories: dict[int, dict]) -> None:
    """Сохранить категории."""
    items = [categories[key] for key in sorted(categories)]
    save_json("categories.json", items)


def load_users() -> dict[int, dict]:
    """Загрузить пользователей."""
    raw = load_json("users.json", [])
    return {int(item["id"]): item for item in raw}


def save_users(users: dict[int, dict]) -> None:
    """Сохранить пользователей."""
    items = [users[key] for key in sorted(users)]
    save_json("users.json", items)


def load_questions() -> list[dict]:
    """Загрузить список вопросов."""
    return load_json("questions.json", [])


def save_questions(questions: list[dict]) -> None:
    """Сохранить список вопросов."""
    save_json("questions.json", questions)


def load_answers() -> list[dict]:
    """Загрузить список ответов."""
    return load_json("answers.json", [])


def save_answers(answers: list[dict]) -> None:
    """Сохранить список ответов."""
    save_json("answers.json", answers)
