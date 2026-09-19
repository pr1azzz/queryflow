"""
QueryFlow — система учета вопросов и ответов.

Точка запуска консольного приложения (ПР2): меню сценариев,
коллекции, модули, JSON-хранилище.
"""

from __future__ import annotations

from datetime import date

from answers import add_answer, count_answers, get_answers_for_question
from categories import (
    add_category,
    filter_active_categories,
    find_category,
    is_category_active,
    sort_categories,
)
from questions import (
    add_question,
    can_publish_question,
    close_question,
    filter_questions_by_category,
    find_questions,
    format_question_card,
    get_question_by_id,
    get_question_status,
    sort_questions_by_date,
)
from storage import (
    load_answers,
    load_categories,
    load_questions,
    load_users,
    save_answers,
    save_categories,
    save_questions,
    save_users,
)
from users import add_user, get_user_name, normalize_role
from utils import configure_console, input_choice, input_int, input_nonempty


def show_question_ids(questions: list[dict]) -> None:
    """Краткий список id вопросов — чтобы не путать с id категорий."""
    if not questions:
        print("Вопросы отсутствуют.")
        return
    print("Доступные вопросы (id):")
    for item in sort_questions_by_date(questions):
        preview = item["text"].strip()
        if len(preview) > 40:
            preview = preview[:37] + "..."
        print(f"  {item['id']}: {preview}")


def show_categories(categories: dict[int, dict]) -> None:
    """Вывести список категорий."""
    if not categories:
        print("Категории отсутствуют.")
        return
    print("\nID | Название | Активна")
    print("-" * 40)
    for category in sort_categories(categories):
        active = "да" if category["is_active"] else "нет"
        print(f"{category['id']:<2} | {category['name']:<20} | {active}")


def show_questions(
    questions: list[dict],
    categories: dict[int, dict],
    users: dict[int, dict],
    answers: list[dict],
) -> None:
    """Вывести список вопросов с статусами."""
    if not questions:
        print("Вопросы отсутствуют.")
        return
    print()
    for item in sort_questions_by_date(questions):
        category = categories.get(item["category_id"], {})
        category_name = category.get("name", "?")
        author = get_user_name(users, item["author_id"])
        status = get_question_status(
            item["is_closed"],
            count_answers(answers, item["id"]),
        )
        created = date.fromisoformat(item["created_on"])
        print(format_question_card(
            author=author,
            category=category_name,
            text=item["text"],
            status=status,
            created_on=created,
        ))
        print(f"(id={item['id']})")
        print("-" * 40)


def show_answers_for_question(
    answers: list[dict],
    users: dict[int, dict],
    question_id: int,
) -> None:
    """Вывести ответы на выбранный вопрос."""
    items = get_answers_for_question(answers, question_id)
    if not items:
        print("Ответов пока нет.")
        return
    for item in items:
        author = get_user_name(users, item["author_id"])
        print(f"[{item['created_on']}] {author}: {item['text']}")


def _pick_user(users: dict[int, dict]) -> int:
    print("\nПользователи:")
    for user in users.values():
        print(f"  {user['id']}. {user['name']} ({user['role']})")
    return input_int("ID пользователя: ")


def action_add_category(categories: dict[int, dict]) -> None:
    name = input_nonempty("Название категории: ")
    add_category(categories, name, is_active=True)
    save_categories(categories)
    print("Категория добавлена.")


def action_find_category(categories: dict[int, dict]) -> None:
    query = input_nonempty("Поиск (название или id): ")
    found = find_category(categories, query)
    if not found:
        print("Ничего не найдено. Подсказка: ищите по названию "
              "(например «Python») или по id (например «4»).")
        return
    for item in found:
        print(f"{item['id']}: {item['name']}")


def action_add_question(
    questions: list[dict],
    categories: dict[int, dict],
    users: dict[int, dict],
) -> None:
    show_categories(categories)
    category_id = input_int("ID категории: ")
    if category_id not in categories:
        print("Категория не найдена.")
        return
    if not is_category_active(categories, category_id):
        print("Публикация отклонена: категория неактивна.")
        return
    text = input_nonempty("Текст вопроса: ")
    if not can_publish_question(text, True):
        print("Публикация отклонена: слишком короткий текст.")
        return
    author_id = _pick_user(users)
    if author_id not in users:
        print("Пользователь не найден.")
        return
    question = add_question(questions, text, category_id, author_id)
    save_questions(questions)
    print(f"Вопрос опубликован (id={question['id']}).")


def action_add_answer(
    questions: list[dict],
    answers: list[dict],
    users: dict[int, dict],
) -> None:
    show_question_ids(questions)
    question_id = input_int("ID вопроса: ")
    question = get_question_by_id(questions, question_id)
    if question is None:
        print("Вопрос не найден. Сначала посмотрите список (пункт 5).")
        return
    if question["is_closed"]:
        print("Нельзя ответить: вопрос закрыт.")
        return
    text = input_nonempty("Текст ответа: ")
    author_id = _pick_user(users)
    if author_id not in users:
        print("Пользователь не найден.")
        return
    answer = add_answer(answers, question_id, text, author_id)
    save_answers(answers)
    print(f"Ответ добавлен (id={answer['id']}).")


def action_check_status(
    questions: list[dict],
    answers: list[dict],
) -> None:
    show_question_ids(questions)
    question_id = input_int("ID вопроса: ")
    question = get_question_by_id(questions, question_id)
    if question is None:
        print("Вопрос не найден. Сначала посмотрите список (пункт 5).")
        return
    status = get_question_status(
        question["is_closed"],
        count_answers(answers, question_id),
    )
    print(f"Статус: {status}")


def action_filter_by_category(
    questions: list[dict],
    categories: dict[int, dict],
    users: dict[int, dict],
    answers: list[dict],
) -> None:
    show_categories(categories)
    category_id = input_int("ID категории: ")
    filtered = filter_questions_by_category(questions, category_id)
    show_questions(filtered, categories, users, answers)


def action_find_questions(
    questions: list[dict],
    categories: dict[int, dict],
    users: dict[int, dict],
    answers: list[dict],
) -> None:
    query = input_nonempty("Подстрока поиска: ")
    found = find_questions(questions, query)
    show_questions(found, categories, users, answers)


def action_close_question(questions: list[dict]) -> None:
    show_question_ids(questions)
    question_id = input_int("ID вопроса: ")
    if close_question(questions, question_id):
        save_questions(questions)
        print("Вопрос закрыт.")
    else:
        print("Вопрос не найден. Сначала посмотрите список (пункт 5).")


def action_add_user(users: dict[int, dict]) -> None:
    name = input_nonempty("Имя пользователя: ")
    while True:
        role_raw = input_nonempty("Роль (user/moderator): ")
        role = normalize_role(role_raw)
        if role is not None:
            break
        print("Ошибка: роль должна быть user или moderator.")
    user = add_user(users, name, role)
    save_users(users)
    print(f"Пользователь добавлен (id={user['id']}).")


def action_show_active_categories(categories: dict[int, dict]) -> None:
    active = filter_active_categories(categories)
    if not active:
        print("Активных категорий нет.")
        return
    for item in active:
        print(f"{item['id']}: {item['name']}")


def print_menu() -> None:
    print("\n=== QueryFlow: учёт вопросов и ответов ===")
    print("1. Показать категории")
    print("2. Показать активные категории")
    print("3. Найти категорию")
    print("4. Добавить категорию")
    print("5. Показать вопросы")
    print("6. Найти вопрос")
    print("7. Вопросы по категории")
    print("8. Опубликовать вопрос")
    print("9. Проверить статус вопроса")
    print("10. Закрыть вопрос")
    print("11. Показать ответы на вопрос")
    print("12. Добавить ответ")
    print("13. Добавить пользователя")
    print("0. Выход")


def main() -> None:
    """Точка запуска: цикл меню и вызов функций проекта."""
    configure_console()
    categories = load_categories()
    users = load_users()
    questions = load_questions()
    answers = load_answers()

    while True:
        print_menu()
        choice = input_choice("Выберите действие: ")
        if not choice:
            continue
        if choice == "0":
            print("До свидания!")
            break
        if choice == "1":
            show_categories(categories)
        elif choice == "2":
            action_show_active_categories(categories)
        elif choice == "3":
            action_find_category(categories)
        elif choice == "4":
            action_add_category(categories)
        elif choice == "5":
            show_questions(questions, categories, users, answers)
        elif choice == "6":
            action_find_questions(
                questions, categories, users, answers,
            )
        elif choice == "7":
            action_filter_by_category(
                questions, categories, users, answers,
            )
        elif choice == "8":
            action_add_question(questions, categories, users)
        elif choice == "9":
            action_check_status(questions, answers)
        elif choice == "10":
            action_close_question(questions)
        elif choice == "11":
            show_question_ids(questions)
            qid = input_int("ID вопроса: ")
            if get_question_by_id(questions, qid) is None:
                print("Вопрос не найден. Сначала посмотрите список (пункт 5).")
            else:
                show_answers_for_question(answers, users, qid)
        elif choice == "12":
            action_add_answer(questions, answers, users)
        elif choice == "13":
            action_add_user(users)
        else:
            print("Неизвестный пункт меню. Введите номер от 0 до 13.")


if __name__ == "__main__":
    main()
