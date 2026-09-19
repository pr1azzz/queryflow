"""
QueryFlow — начальный сценарий ПР1.
Система учета вопросов и ответов.

Используются простые типы данных, операции, преобразование типов,
ветвления, функции и импорт стандартного модуля.
"""

from datetime import date


def can_publish_question(text: str, category_active: bool, min_length: int = 10) -> bool:
    """Проверяет, можно ли опубликовать вопрос."""
    cleaned = text.strip()
    text_length = len(cleaned)
    if not category_active:
        return False
    if text_length < min_length:
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


def main() -> None:
    # Сущности предметной области (простые типы, без классов — уровень ПР1)
    user_name = "Иван Петров"
    user_is_moderator = False

    category_name = "Python"
    category_is_active = True

    question_text = "  Как работает виртуальное окружение в Python?  "
    question_is_closed = False
    answers_count_raw = "0"  # имитация ввода/данных как строки
    answers_count = int(answers_count_raw)  # преобразование типов
    created_on = date(2026, 9, 19)

    publishable = can_publish_question(question_text, category_is_active)
    status = get_question_status(question_is_closed, answers_count)

    print("=== QueryFlow: учёт вопросов и ответов ===")
    print(f"Автор: {user_name}")
    print(f"Модератор: {user_is_moderator}")
    print(f"Категория: {category_name} (активна: {category_is_active})")
    print(f"Число ответов: {answers_count}")
    print()

    if publishable:
        print("Публикация вопроса: разрешена")
        print()
        print(format_question_card(
            author=user_name,
            category=category_name,
            text=question_text,
            status=status,
            created_on=created_on,
        ))
    else:
        print("Публикация вопроса: отклонена")
        if not category_is_active:
            print("Причина: категория неактивна")
        elif len(question_text.strip()) < 10:
            print("Причина: слишком короткий текст вопроса")


if __name__ == "__main__":
    main()
