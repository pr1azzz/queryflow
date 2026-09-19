"""Тесты функций категорий."""

from categories import (
    add_category,
    filter_active_categories,
    find_category,
    is_category_active,
)


def test_add_category() -> None:
    categories: dict[int, dict] = {}
    add_category(categories, "Python")
    assert len(categories) == 1
    assert categories[1]["name"] == "Python"


def test_find_category() -> None:
    categories: dict[int, dict] = {}
    add_category(categories, "Python")
    add_category(categories, "Django")
    found = find_category(categories, "py")
    assert len(found) == 1
    assert found[0]["name"] == "Python"
    by_id = find_category(categories, "2")
    assert len(by_id) == 1
    assert by_id[0]["name"] == "Django"


def test_is_category_active() -> None:
    categories: dict[int, dict] = {}
    add_category(categories, "Архив", is_active=False)
    assert not is_category_active(categories, 1)


def test_filter_active_categories() -> None:
    categories: dict[int, dict] = {}
    add_category(categories, "Python", True)
    add_category(categories, "Архив", False)
    active = filter_active_categories(categories)
    assert len(active) == 1
    assert active[0]["name"] == "Python"
