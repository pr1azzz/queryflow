"""Функции работы с пользователями."""

from __future__ import annotations


ALLOWED_ROLES = frozenset({"user", "moderator"})


def normalize_role(role: str) -> str | None:
    """Вернуть нормализованную роль или None, если роль недопустима."""
    cleaned = role.strip().lower()
    if cleaned in ALLOWED_ROLES:
        return cleaned
    return None


def add_user(
    users: dict[int, dict],
    name: str,
    role: str = "user",
) -> dict:
    """Добавить пользователя."""
    new_id = max(users.keys(), default=0) + 1
    normalized = normalize_role(role) or "user"
    user = {
        "id": new_id,
        "name": name.strip(),
        "role": normalized,
    }
    users[new_id] = user
    return user


def find_users(users: dict[int, dict], query: str) -> list[dict]:
    """Найти пользователей по подстроке имени."""
    needle = query.strip().lower()
    return [
        user for user in users.values()
        if needle in user["name"].lower()
    ]


def get_user_name(users: dict[int, dict], user_id: int) -> str:
    """Вернуть имя пользователя или заглушку."""
    user = users.get(user_id)
    if user is None:
        return f"user#{user_id}"
    return user["name"]
