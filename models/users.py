"""Класс User и функции работы с коллекцией пользователей."""

from __future__ import annotations


ALLOWED_ROLES = frozenset({"user", "moderator"})


class User:
    """Пользователь системы учёта вопросов и ответов."""

    def __init__(
        self,
        user_id: int,
        name: str,
        role: str = "user",
    ) -> None:
        """Создать объект пользователя."""
        self.id = user_id
        self.name = name.strip()
        self.role = normalize_role(role) or "user"

    @classmethod
    def from_data(cls, data: dict) -> User:
        """Создать пользователя из набора данных (JSON)."""
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            role=str(data.get("role", "user")),
        )

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"{self.name} ({self.role})"


def normalize_role(role: str) -> str | None:
    """Вернуть нормализованную роль или None, если роль недопустима."""
    cleaned = role.strip().lower()
    if cleaned in ALLOWED_ROLES:
        return cleaned
    return None


def add_user(
    users: list[User],
    name: str,
    role: str = "user",
) -> User:
    """Создать объект User и добавить его в коллекцию."""
    new_id = max((item.id for item in users), default=0) + 1
    user = User(new_id, name, role)
    users.append(user)
    return user


def get_user_by_id(users: list[User], user_id: int) -> User | None:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def find_users(users: list[User], query: str) -> list[User]:
    """Найти пользователей по подстроке имени."""
    needle = query.strip().lower()
    return [user for user in users if needle in user.name.lower()]


def get_user_name(users: list[User], user_id: int) -> str:
    """Вернуть имя пользователя или заглушку."""
    user = get_user_by_id(users, user_id)
    if user is None:
        return f"user#{user_id}"
    return user.name


def show_users(users: list[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователи отсутствуют.")
        return
    for user in users:
        print(f"  {user.id}. {user}")
