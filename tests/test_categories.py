"""Тесты категорий (объектная модель ПР3)."""

from models import Category
from models.categories import (
    add_category,
    filter_active_categories,
    find_category,
    is_category_active,
)


def test_category_creation() -> None:
    category = Category(1, "Python", True)
    assert category.id == 1
    assert category.name == "Python"
    assert category.is_active
    assert category.is_available()
    assert "Python" in str(category)


def test_category_validate_name() -> None:
    assert Category.validate_name("Django")
    assert not Category.validate_name("   ")


def test_add_category() -> None:
    categories: list[Category] = []
    item = add_category(categories, "Python")
    assert len(categories) == 1
    assert item.name == "Python"
    assert isinstance(item, Category)


def test_find_category() -> None:
    categories: list[Category] = []
    add_category(categories, "Python")
    add_category(categories, "Django")
    found = find_category(categories, "py")
    assert len(found) == 1
    assert found[0].name == "Python"
    by_id = find_category(categories, "2")
    assert len(by_id) == 1
    assert by_id[0].name == "Django"


def test_is_category_active() -> None:
    categories: list[Category] = []
    add_category(categories, "Архив", is_active=False)
    assert not is_category_active(categories, 1)


def test_filter_active_categories() -> None:
    categories: list[Category] = []
    add_category(categories, "Python", True)
    add_category(categories, "Архив", False)
    active = filter_active_categories(categories)
    assert len(active) == 1
    assert active[0].name == "Python"
