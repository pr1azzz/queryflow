"""Класс Category и функции работы с коллекцией категорий."""

from __future__ import annotations


class Category:
    """Категория вопросов."""

    def __init__(
        self,
        category_id: int,
        name: str,
        is_active: bool = True,
    ) -> None:
        """Создать объект категории."""
        self.id = category_id
        self.name = name.strip()
        self.is_active = is_active

    def is_available(self) -> bool:
        """Проверить, доступна ли категория для публикации вопросов."""
        return bool(self.is_active)

    @staticmethod
    def validate_name(name: str) -> bool:
        """Проверить корректность названия категории."""
        return bool(name.strip())

    def __str__(self) -> str:
        """Вернуть строковое представление категории."""
        status = "активна" if self.is_active else "неактивна"
        return f"{self.name} ({status})"


def add_category(
    categories: list[Category],
    name: str,
    is_active: bool = True,
) -> Category:
    """Создать объект Category и добавить его в коллекцию."""
    new_id = max((item.id for item in categories), default=0) + 1
    category = Category(new_id, name, is_active)
    categories.append(category)
    return category


def get_category_by_id(
    categories: list[Category],
    category_id: int,
) -> Category | None:
    """Найти категорию по идентификатору."""
    for category in categories:
        if category.id == category_id:
            return category
    return None


def find_category(
    categories: list[Category],
    query: str,
) -> list[Category]:
    """Найти категории по подстроке названия или точному id."""
    needle = query.strip().lower()
    if not needle:
        return []
    result: list[Category] = []
    seen: set[int] = set()
    if needle.isdigit():
        by_id = get_category_by_id(categories, int(needle))
        if by_id is not None:
            result.append(by_id)
            seen.add(by_id.id)
    for category in categories:
        if category.id in seen:
            continue
        if needle in category.name.lower():
            result.append(category)
    return result


def is_category_active(
    categories: list[Category],
    category_id: int,
) -> bool:
    """Проверить, активна ли категория (через метод объекта)."""
    category = get_category_by_id(categories, category_id)
    if category is None:
        return False
    return category.is_available()


def filter_active_categories(
    categories: list[Category],
) -> list[Category]:
    """Отобрать только активные категории."""
    return [item for item in categories if item.is_available()]


def sort_categories(categories: list[Category]) -> list[Category]:
    """Отсортировать категории по названию."""
    return sorted(categories, key=lambda item: item.name.lower())


def show_categories(categories: list[Category]) -> None:
    """Вывести список категорий."""
    if not categories:
        print("Категории отсутствуют.")
        return
    print("\nID | Название | Активна")
    print("-" * 40)
    for category in sort_categories(categories):
        active = "да" if category.is_active else "нет"
        print(f"{category.id:<2} | {category.name:<20} | {active}")
