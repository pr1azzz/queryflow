# QueryFlow — система учёта вопросов и ответов

Индивидуальный проект №245 по дисциплине «Технологии разработки приложений
на базе фреймворков». Коржов Сергей Сергеевич, ЭФБО-13-24.
Текущий этап — ПР7: Django-шаблоны и самостоятельный SQL-слой на SQLite.

## Запуск (PowerShell, из корня проекта)

Python 3.11+, Django 5.2, Bootstrap 5.3.3, pytest, flake8.
`sqlite3` входит в стандартную библиотеку Python.

```powershell
# Только если виртуального окружения ещё нет:
py -3.11 -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe -m db.import_json
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Открыть <http://127.0.0.1:8000/>. Остановка — `Ctrl+C`.
Если порт занят ранее запущенным сервером, остановить его в его терминале
или указать другой порт: `python manage.py runserver 8007`.
Для загрузки Bootstrap через CDN нужен интернет.

В проекте **две разные базы**:

- `db.sqlite3` — служебные таблицы Django; создаются `manage.py migrate`,
  файл не включён в Git.
- `data/queryflow.sqlite` — предметные таблицы ПР7; создаются обычным SQL,
  включены в сдаваемые материалы. Django ORM для этих таблиц не используется.

## Реализованные страницы и сценарии

| URL | Представление | Сценарий |
| --- | --- | --- |
| `/` | `homepage.views.index` | Главная и навигация |
| `/questions/` | `questions.views.questions` | Все вопросы с категориями, авторами и статусами |
| `/questions/open/` | `questions.views.open_questions` | Незакрытые вопросы |
| `/questions/unanswered/` | `questions.views.unanswered_questions` | Открытые вопросы без ответов |
| `/questions/search/` | `questions.views.search` | Поиск по тексту, категории и начальной дате |
| `/questions/statistics/` | `questions.views.statistics` | Итоги, вопросы по категориям, ответы по участникам |
| `/questions/<int:question_id>/` | `questions.views.question_detail` | Вопрос и его ответы |
| `/categories/` | `categories.views.categories` | Все категории |
| `/categories/active/` | `categories.views.active_categories` | Активные категории |
| `/categories/<int:category_id>/` | `categories.views.category_detail` | Категория и вопросы этой темы |
| `/answers/` | `answers.views.answers` | Ответы, связанные вопросы и авторы |
| `/answers/<int:answer_id>/` | `answers.views.answer_detail` | Карточка ответа |

Все страницы данных используют SQLite. Сохранены старые URL ПР5–ПР6.
Отсутствующие объекты и неизвестные пути возвращают HTTP 404.
`/admin/` остаётся служебным маршрутом Django; предметные таблицы в нём
не зарегистрированы. Создание вопросов/ответов через веб-формы не входит
в ПР6–ПР7. Новая форма поиска отправляет GET и не изменяет данные.

Примеры:

- `/questions/search/?q=Python&category=1&since=2026-09-19`;
- `/questions/search/?q=&page=2` — следующая страница выдачи (по 10 вопросов);
- `/questions/statistics/?minimum=1` — категории хотя бы с одним вопросом.

Поиск выполняется по буквальной подстроке через `instr(lower(...), lower(?))`.
Регистр латиницы не учитывается, кириллицы — учитывается (поведение SQLite).
Дата проверяется как `YYYY-MM-DD`; условия объединены `AND`. Неверные
параметры дают понятное сообщение и 400; пустая выдача — сообщение и 200.
Сортировка по дате и ID делает разбиение на страницы устойчивым.

## Структура проекта

```text
queryflow/                 # settings.py, корневой urls.py, ASGI/WSGI
homepage/                  # главная страница и handler404
    templates/homepage/    # index.html
    static/homepage/       # css/style.css, js/main.js, img/logo.svg
questions/                 # вопросы, поиск, статистика
    templates/questions/   # страницы и includes карточки/статуса
categories/                # категории и их вопросы
answers/                   # ответы со связанными данными
    templates/answers/     # страницы и includes/answer_card.html
templates/                 # base.html, 404.html, includes/navigation.html
db/
    database.py            # get_connection(), initialize_database()
    import_json.py         # импорт четырёх JSON-файлов одной транзакцией
    queries.py             # исполнение именованных запросов из SQL-файла
sql/
    schema.sql             # таблицы, ограничения и индексы
    queries.sql            # 18 запросов с назначением и параметрами
data/
    queryflow.sqlite       # предметная база ПР7
    *.json                 # исходные данные ПР3–ПР6, сохранены
models/                    # обычные Python-классы ПР3
storage.py                 # прежняя загрузка/сохранение JSON
main.py                    # прежняя консольная версия
manage.py                  # команды Django
tests/                     # предметные, шаблонные, HTTP- и SQL-проверки
docs/                      # отчёты по практическим
шпаргалка_пр6.md
шпаргалка_пр7.md
```

## Результат ПР6: шаблоны

HTML вынесен из Python, функция `page()` удалена. Представления вызывают
`render(request, template, context)`. `templates/base.html` задаёт общий
каркас и блоки `title`, `content`; дочерние страницы используют `extends`.
Навигация, карточки и статусы подключаются через `include ... with ... only`.
Списки используют `for/empty`, состояния — `if/elif/else`.
Есть фильтры `length`, `default`, `truncatechars`, `stringformat`.
Ссылки строятся через `{% url %}` и `app_name` приложений.

`DIRS=[BASE_DIR / "templates"]` находит общие шаблоны,
`APP_DIRS=True` — шаблоны зарегистрированных приложений.
DTL автоматически экранирует текст. Собственные CSS, SVG-изображение и JS
подключены через `{% load static %}` / `{% static %}`; JS показывает год
в подвале. Bootstrap сохранён для адаптивной сетки и компонентов.

Самостоятельное состояние ПР6 зафиксировано коммитом `c921528`
(`PR6: migrate pages to Django templates`). На этом этапе view читали JSON
и передавали объекты ПР3. В ПР7 те же шаблоны адаптированы к `sqlite3.Row`:
например, `question.author.name` заменено на `question.author_name`.

## Результат ПР7: схема и ключи

| Таблица | Поля и типы | Связи |
| --- | --- | --- |
| `categories` | `id INTEGER PK`, `name TEXT`, `is_active INTEGER` | Категории вопросов |
| `users` | `id INTEGER PK`, `name TEXT`, `role TEXT` | Авторы вопросов и ответов |
| `questions` | `id INTEGER PK`, `text TEXT`, `category_id INTEGER`, `author_id INTEGER`, `is_closed INTEGER`, `created_on TEXT` | FK на `categories.id`, `users.id` |
| `answers` | `id INTEGER PK`, `text TEXT`, `question_id INTEGER`, `author_id INTEGER`, `created_on TEXT` | FK на `questions.id`, `users.id` |

Даты хранятся в ISO-формате; логические признаки — 0/1.
`NOT NULL`, `CHECK`, первичные и внешние ключи ограничивают некорректные данные.
`ON DELETE RESTRICT` запрещает удалять родителя связанной записи.
Каждое подключение включает `PRAGMA foreign_keys=ON` и `sqlite3.Row`.
Индексы добавлены на внешние ключи. Пути вычисляются от файлов модулей,
поэтому доступ к базе не зависит от рабочей папки.

## Создание и импорт

```powershell
# Только схема; повторный запуск не удаляет данные:
.\.venv\Scripts\python.exe -m db.database
# Схема + перенос данных:
.\.venv\Scripts\python.exe -X utf8 -m db.import_json
```

Сначала читаются и проверяются все JSON-файлы. Импорт выполняется в порядке
`categories → users → questions → answers`, чтобы родители существовали
до дочерних записей. `executemany()` передаёт значения через `?`.
Все вставки/обновления объединены в транзакцию: успех — commit, ошибка — rollback.
Повторный запуск обновляет совпавшие ID через `ON CONFLICT(id) DO UPDATE`,
не создаёт дубликаты и **не удаляет** записи SQLite, которых нет в JSON.
Противоречивые ссылки и повторные ID в исходном файле обнаруживаются.

После исходного импорта: 6 категорий, 4 пользователя, 2 вопроса, 1 ответ.
JSON и SQLite теперь независимы: консоль записывает JSON; чтобы перенести
его новые значения в сайт, нужно явно повторить импорт. Автоматической
двусторонней синхронизации нет. Это позволяет сохранить прежний код ПР3.

## Запросы и их использование

Все 18 запросов хранятся в `sql/queries.sql`. Метка `-- name:` позволяет
`db/queries.py` читать и исполнять именно этот SQL без копирования во view.
Имена запросов выбираются кодом, значения передаются отдельно параметрами.

| № | Запрос | Использование |
| --- | --- | --- |
| 1 | `category_list` — SELECT списка | Категории и форма поиска |
| 2 | `user_list` — SELECT списка | Участники на странице статистики |
| 3 | `active_categories` — WHERE | Активные категории |
| 4 | `open_questions` — WHERE | Открытые вопросы |
| 5 | `question_list` — JOIN | Вопросы, категории, авторы |
| 6 | `answer_list` — JOIN | Ответы, вопросы, категории, авторы |
| 7 | `question_summary` — COUNT/SUM | Число всех, открытых и закрытых вопросов |
| 8 | `answer_summary` — COUNT/DISTINCT | Число ответов и ответивших авторов |
| 9 | `category_statistics` — LEFT JOIN/GROUP BY/HAVING | Вопросы по категориям с порогом |
| 10 | `author_statistics` — LEFT JOIN/GROUP BY | Ответы по участникам, включая ноль |
| 11 | `question_search` — WHERE/LIMIT/OFFSET | Поиск и постраничный вывод |
| 12 | `search_count` — COUNT/WHERE | Общее количество результатов поиска |
| 13 | `question_detail` | Карточка вопроса |
| 14 | `question_answers` | Ответы выбранного вопроса |
| 15 | `category_detail` | Карточка категории |
| 16 | `category_questions` | Вопросы выбранной категории |
| 17 | `answer_detail` | Карточка ответа |
| 18 | `unanswered_questions` — NOT EXISTS | Открытые вопросы без ответов |

Таким образом, минимум «10 запросов, по два каждого из пяти видов» выполнен.
Все запросы используются веб-страницами. `LEFT JOIN` и `COUNT(q.id)`
сохраняют категории с нулём вопросов; `HAVING` фильтрует уже полученные группы.

Путь запроса: GET-параметры → проверка в `questions.views.search()` →
`fetch_all('question_search', parameters)` → `connection.execute(SQL, parameters)`
→ `list[sqlite3.Row]` → словарь контекста → Django-шаблон → HTML.
Соединения закрываются через `contextlib.closing`, в том числе при исключениях.

## Проверка SQL вручную

Локально установлен SQLite CLI в `.venv/tools/sqlite/sqlite3.exe`:

```powershell
.\.venv\tools\sqlite\sqlite3.exe data/queryflow.sqlite
```

Внутри CLI можно выполнить `.tables`, `.schema`, запрос из `queries.sql`,
например `SELECT COUNT(*) FROM questions;`, и выйти командой `.quit`.
Заполнители `?` требуют значений (команда CLI `.parameter set ?1 1`).
CLI не входит в Git; на другом компьютере можно установить его
с [официального сайта SQLite](https://sqlite.org/download.html).
Для просмотра таблиц в VS Code используется SQLite Viewer.

Без CLI запросы можно выполнять через модуль проекта:

```powershell
.\.venv\Scripts\python.exe -X utf8 -c "from db.queries import fetch_all; print([dict(r) for r in fetch_all('category_statistics', (0,))])"
```

## Проверки и 404

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m flake8 .
.\.venv\Scripts\python.exe main.py
```

ПР6: 55 тестов. ПР7: **84 теста**, включая 23 неизменённых теста ПР3;
`check` и flake8 — без замечаний. Проверены все 18 запросов через SQLite CLI,
сравнение с Python, целостность БД, импорт/повторный импорт/откат,
JOIN, нулевые группы, HAVING, безопасные параметры, поиск, пагинация,
пустые результаты, экранирование и отсутствие записи при GET.
В браузере проверены страницы, формы поиска и статистики, переходы,
404 и ширина 390 px.

По умолчанию `DEBUG=True`. Для демонстрации общей страницы 404:

```powershell
$env:DJANGO_DEBUG = "False"
.\.venv\Scripts\python.exe manage.py runserver --insecure
# После остановки:
Remove-Item Env:DJANGO_DEBUG
```

`--insecure` здесь нужен только для локальной раздачи CSS при `DEBUG=False`.
Явный ответ отсутствующего объекта имеет 404 в обоих режимах.
Настройки предназначены для локальной учебной работы.

## Материалы для защиты

- [Шпаргалка ПР6: 25 показателей](шпаргалка_пр6.md).
- [Шпаргалка ПР7: 25 показателей](шпаргалка_пр7.md).
- Отчёт ПР6: `ОТЧЁТ_ПР6_Коржов_С.С_ЭФБО-13-24.docx`.
- Отчёт ПР7: `ОТЧЁТ_ПР7_Коржов_С.С_ЭФБО-13-24.docx`.
- [Репозиторий](https://github.com/pr1azzz/queryflow).

Готовые отчёты ПР6 и ПР7 находятся в общей папке рядом с каталогом `queryflow`.

ПР6 и ПР7 зафиксированы отдельными локальными коммитами `PR6:` и `PR7:`.
Публикация на GitHub — `git push`. Следующий этап — Django ORM и формы.


## ПР9: переход на Django ORM

Веб-часть использует модели Category, participants.User, Question и Answer
в db.sqlite3. Участники предметной области отделены от учётных записей Django.
База data/queryflow.sqlite, SQL и JSON ПР7 сохранены как учебный этап;
изменения в них автоматически в веб-интерфейс больше не попадают.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py import_legacy
.\.venv\Scripts\python.exe manage.py orm_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Импорт читает источник только для чтения, переносит записи атомарно, сохраняет
ID и связи, пропускает уже существующие ID (не перезаписывает изменения ORM).
При конфликте идентификаторов следует использовать чистую базу назначения.
`orm_demo` демонстрирует create/get/save/delete с откатом транзакции.
Запросы находятся в questions/queries.py и views.py приложений. Поиск по тексту,
категории, автору, дате, именам связанных объектов; сортировки по разрешённому
словарю, Paginator и сохранение GET-параметров. В SQLite icontains не меняет
регистр кириллицы. При DEBUG=True доступна локальная Django Debug Toolbar.

Проверки: `python manage.py check`, `python manage.py makemigrations --check`,
`python -m pytest`, `python -m flake8`.
