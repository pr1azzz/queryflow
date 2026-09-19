"""Функции работы с категориями вопросов."""

from __future__ import annotations


def add_category(
    categories: dict[int, dict],
    name: str,
    is_active: bool = True,
) -> dict:
    """Добавить категорию в словарь categories."""
    new_id = max(categories.keys(), default=0) + 1
    category = {
        "id": new_id,
        "name": name.strip(),
        "is_active": is_active,
    }
    categories[new_id] = category
    return category


def find_category(
    categories: dict[int, dict],
    query: str,
) -> list[dict]:
    """Найти категории по подстроке названия или точному id."""
    needle = query.strip().lower()
    if not needle:
        return []
    result = []
    seen: set[int] = set()
    if needle.isdigit():
        by_id = categories.get(int(needle))
        if by_id is not None:
            result.append(by_id)
            seen.add(by_id["id"])
    for category in categories.values():
        if category["id"] in seen:
            continue
        if needle in category["name"].lower():
            result.append(category)
    return result


def is_category_active(
    categories: dict[int, dict],
    category_id: int,
) -> bool:
    """Проверить, активна ли категория."""
    category = categories.get(category_id)
    if category is None:
        return False
    return bool(category["is_active"])


def filter_active_categories(
    categories: dict[int, dict],
) -> list[dict]:
    """Отобрать только активные категории."""
    return [
        category
        for category in categories.values()
        if category["is_active"]
    ]


def sort_categories(
    categories: dict[int, dict],
) -> list[dict]:
    """Отсортировать категории по названию."""
    return sorted(
        categories.values(),
        key=lambda item: item["name"].lower(),
    )
