"""Тесты пользователей (объектная модель ПР3)."""

from models import User
from models.users import add_user, find_users


def test_user_creation() -> None:
    user = User(1, "Иван Петров", "user")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.role == "user"
    assert "Иван" in str(user)


def test_user_from_data() -> None:
    user = User.from_data({
        "id": 2,
        "name": "Анна Смирнова",
        "role": "moderator",
    })
    assert user.id == 2
    assert user.name == "Анна Смирнова"
    assert user.role == "moderator"


def test_add_user() -> None:
    users: list[User] = []
    item = add_user(users, "Сергей", "user")
    assert len(users) == 1
    assert item.id == 1
    assert isinstance(item, User)


def test_find_users() -> None:
    users: list[User] = []
    add_user(users, "Иван Петров")
    add_user(users, "Анна Смирнова")
    found = find_users(users, "анна")
    assert len(found) == 1
    assert found[0].name == "Анна Смирнова"
