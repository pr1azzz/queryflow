"""
QueryFlow — система учета вопросов и ответов.

Точка запуска консольного приложения (ПР3): объектная модель,
коллекции объектов, модули, JSON-хранилище.
"""

from __future__ import annotations

from datetime import date

from models import Answer, Category, Question, User
from models.answers import (
    add_answer,
    count_answers,
    get_answers_for_question,
)
from models.categories import (
    add_category,
    filter_active_categories,
    find_category,
    get_category_by_id,
    show_categories,
)
from models.questions import (
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
from models.users import (
    add_user,
    get_user_by_id,
    normalize_role,
    show_users,
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
from utils import configure_console, input_choice, input_int, input_nonempty


def show_question_ids(questions: list[Question]) -> None:
    """Краткий список id вопросов — чтобы не путать с id категорий."""
    if not questions:
        print("Вопросы отсутствуют.")
        return
    print("Доступные вопросы (id):")
    for item in sort_questions_by_date(questions):
        preview = item.text
        if len(preview) > 40:
            preview = preview[:37] + "..."
        print(f"  {item.id}: {preview}")


def show_questions(
    questions: list[Question],
    answers: list[Answer],
) -> None:
    """Вывести список вопросов с статусами (через объекты)."""
    if not questions:
        print("Вопросы отсутствуют.")
        return
    print()
    for item in sort_questions_by_date(questions):
        status = get_question_status(
            item.is_closed,
            count_answers(answers, item.id),
        )
        created = date.fromisoformat(item.created_on)
        print(format_question_card(
            author=item.author.name,
            category=item.category.name,
            text=item.text,
            status=status,
            created_on=created,
        ))
        print(f"(id={item.id})")
        print("-" * 40)


def show_answers_for_question(
    answers: list[Answer],
    question_id: int,
) -> None:
    """Вывести ответы на выбранный вопрос."""
    items = get_answers_for_question(answers, question_id)
    if not items:
        print("Ответов пока нет.")
        return
    for item in items:
        print(item)


def action_add_category(categories: list[Category]) -> None:
    """Сценарий: добавить категорию."""
    name = input_nonempty("Название категории: ")
    if not Category.validate_name(name):
        print("Некорректное название категории.")
        return
    add_category(categories, name, is_active=True)
    save_categories(categories)
    print("Категория добавлена.")


def action_find_category(categories: list[Category]) -> None:
    """Сценарий: найти категорию."""
    query = input_nonempty("Поиск (название или id): ")
    found = find_category(categories, query)
    if not found:
        print("Ничего не найдено. Подсказка: ищите по названию "
              "(например «Python») или по id (например «4»).")
        return
    for item in found:
        print(f"{item.id}: {item}")


def action_add_question(
    questions: list[Question],
    categories: list[Category],
    users: list[User],
) -> None:
    """Сценарий: опубликовать вопрос (связь Category + User)."""
    show_categories(categories)
    category_id = input_int("ID категории: ")
    category = get_category_by_id(categories, category_id)
    if category is None:
        print("Категория не найдена.")
        return
    if not category.is_available():
        print("Публикация отклонена: категория неактивна.")
        return
    text = input_nonempty("Текст вопроса: ")
    if not can_publish_question(text, True):
        print("Публикация отклонена: слишком короткий текст.")
        return
    show_users(users)
    author_id = input_int("ID пользователя: ")
    author = get_user_by_id(users, author_id)
    if author is None:
        print("Пользователь не найден.")
        return
    question = add_question(questions, text, category, author)
    if question is None:
        print("Публикация отклонена.")
        return
    save_questions(questions)
    print(f"Вопрос опубликован (id={question.id}).")


def action_add_answer(
    questions: list[Question],
    answers: list[Answer],
    users: list[User],
) -> None:
    """Сценарий: добавить ответ (связь Question + User)."""
    show_question_ids(questions)
    question_id = input_int("ID вопроса: ")
    question = get_question_by_id(questions, question_id)
    if question is None:
        print("Вопрос не найден. Сначала посмотрите список (пункт 5).")
        return
    if question.is_closed:
        print("Нельзя ответить: вопрос закрыт.")
        return
    text = input_nonempty("Текст ответа: ")
    show_users(users)
    author_id = input_int("ID пользователя: ")
    author = get_user_by_id(users, author_id)
    if author is None:
        print("Пользователь не найден.")
        return
    answer = add_answer(answers, question, text, author)
    if answer is None:
        print("Не удалось добавить ответ.")
        return
    save_answers(answers)
    print(f"Ответ добавлен (id={answer.id}).")


def action_check_status(
    questions: list[Question],
    answers: list[Answer],
) -> None:
    """Сценарий: проверить статус вопроса."""
    show_question_ids(questions)
    question_id = input_int("ID вопроса: ")
    question = get_question_by_id(questions, question_id)
    if question is None:
        print("Вопрос не найден. Сначала посмотрите список (пункт 5).")
        return
    status = question.status_text(count_answers(answers, question_id))
    print(f"Статус: {status}")


def action_filter_by_category(
    questions: list[Question],
    categories: list[Category],
    answers: list[Answer],
) -> None:
    """Сценарий: вопросы по категории."""
    show_categories(categories)
    category_id = input_int("ID категории: ")
    filtered = filter_questions_by_category(questions, category_id)
    show_questions(filtered, answers)


def action_find_questions(
    questions: list[Question],
    answers: list[Answer],
) -> None:
    """Сценарий: поиск вопросов."""
    query = input_nonempty("Подстрока поиска: ")
    found = find_questions(questions, query)
    show_questions(found, answers)


def action_close_question(questions: list[Question]) -> None:
    """Сценарий: закрыть вопрос через метод объекта."""
    show_question_ids(questions)
    question_id = input_int("ID вопроса: ")
    if close_question(questions, question_id):
        save_questions(questions)
        print("Вопрос закрыт.")
    else:
        print("Вопрос не найден. Сначала посмотрите список (пункт 5).")


def action_add_user(users: list[User]) -> None:
    """Сценарий: добавить пользователя."""
    name = input_nonempty("Имя пользователя: ")
    while True:
        role_raw = input_nonempty("Роль (user/moderator): ")
        role = normalize_role(role_raw)
        if role is not None:
            break
        print("Ошибка: роль должна быть user или moderator.")
    user = add_user(users, name, role)
    save_users(users)
    print(f"Пользователь добавлен (id={user.id}).")


def action_show_active_categories(categories: list[Category]) -> None:
    """Сценарий: показать активные категории."""
    active = filter_active_categories(categories)
    if not active:
        print("Активных категорий нет.")
        return
    for item in active:
        print(f"{item.id}: {item}")


def print_menu() -> None:
    """Вывести главное меню."""
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
    """Точка запуска: загрузка объектов, цикл меню, сценарии."""
    configure_console()
    categories = load_categories()
    users = load_users()
    questions = load_questions(categories, users)
    answers = load_answers(questions, users)

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
            show_questions(questions, answers)
        elif choice == "6":
            action_find_questions(questions, answers)
        elif choice == "7":
            action_filter_by_category(questions, categories, answers)
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
                show_answers_for_question(answers, qid)
        elif choice == "12":
            action_add_answer(questions, answers, users)
        elif choice == "13":
            action_add_user(users)
        else:
            print("Неизвестный пункт меню. Введите номер от 0 до 13.")


if __name__ == "__main__":
    main()
