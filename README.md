# QueryFlow — Система учета вопросов и ответов

Веб-приложение на Django 5.2 и консольная версия для учёта вопросов и ответов:
публикация вопросов по категориям, ответы, статусы обсуждения.
ПР5 добавляет веб-слой к объектной модели ПР3. Классы, JSON и консольные
сценарии сохранены. Тема №245, Коржов Сергей Сергеевич, ЭФБО-13-24.

## Текущий этап: ПР6 — шаблоны Django

Веб-страницы переведены на `render(request, template, context)`.
HTML из Python и функция `page()` удалены. Общий каркас —
`templates/base.html`, меню — `templates/includes/navigation.html`.
Шаблоны приложений расположены в `<app>/templates/<app>/`.
Настроены `DIRS=[BASE_DIR / "templates"]` и `APP_DIRS=True`.

Карточки вопросов и ответов, статус вопроса вынесены через `include`.
Используются `extends`, `block`, `for/empty`, `if/elif/else`,
фильтры `length`, `default`, `truncatechars`, именованные URL и namespace.
DTL автоматически экранирует пользовательский текст.
CSS, SVG-логотип и JavaScript находятся в `homepage/static/homepage/`;
JS выводит текущий год в подвале. Статика подключается тегом `static`.

В ПР6 сохранены семь видов страниц, данные JSON, объекты ПР3 и консольная
версия. Веб-форм изменения данных и Django ORM пока нет.
Проверено: 55 тестов, `manage.py check`, flake8, страницы и статические ресурсы.
Для проверки общей 404 установить `$env:DJANGO_DEBUG="False"` и запустить
`python manage.py runserver --insecure` (только локальная демонстрация CSS).
После проверки остановить сервер и выполнить `Remove-Item Env:DJANGO_DEBUG`.

- [Шпаргалка ПР6: 25 пунктов](шпаргалка_пр6.md).
- [Отчёт ПР6](docs/ОТЧЁТ_ПР6_Коржов_С.С_ЭФБО-13-24.docx).

Ниже сохранено описание этапов ПР3–ПР5; формирование строк HTML и `page()`
относятся только к историческому состоянию ПР5, а не к текущему коду.

## ПР5: запуск веб-приложения

Из корня проекта в PowerShell (Python 3.11+):

```powershell
# Если окружения ещё нет: py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Открыть <http://127.0.0.1:8000/>. Остановка — `Ctrl+C`.
При активированном окружении можно писать `python manage.py runserver`.
`migrate` создаёт только служебные таблицы Django в локальном `db.sqlite3`;
данные предметной области остаются в JSON. База исключена из Git.

## ПР5: страницы и представления

| URL | View-функция | Назначение |
| --- | --- | --- |
| `/` | `homepage.views.index` | Описание проекта и навигация |
| `/questions/` | `questions.views.questions` | Вопросы, авторы, категории, статусы |
| `/questions/<int:question_id>/` | `questions.views.question_detail` | Карточка вопроса с ответами |
| `/categories/` | `categories.views.categories` | Категории и их активность |
| `/categories/<int:category_id>/` | `categories.views.category_detail` | Категория и её вопросы |
| `/answers/` | `answers.views.answers` | Ответы участников |
| `/answers/<int:answer_id>/` | `answers.views.answer_detail` | Ответ, автор и исходный вопрос |
| Неизвестный URL | `homepage.views.page_not_found` | Общая 404 при `DEBUG=False` |

`/admin/` — служебный маршрут Django; управление сущностями ПР3 через него
пока не реализовано. В браузере доступен просмотр. Добавление, поиск,
редактирование состояния и сохранение данных выполняются в консольной версии.

## ПР5: структура и обработка запроса

```text
manage.py                  # управляющие команды Django
queryflow/
    settings.py            # настройки и INSTALLED_APPS
    urls.py                # include() приложений и handler404
    asgi.py, wsgi.py        # точки входа серверов
homepage/                  # index(), page(), page_not_found()
questions/                 # список и карточка вопроса
categories/                # список и карточка категории
answers/                   # список и карточка ответа
tests/test_web.py          # HTTP-проверки ПР5
шпаргалка_пр5.md # подготовка к защите
```

В приложениях есть `apps.py`, `urls.py`, `views.py`, заготовки `models.py`,
`admin.py` и `migrations/`. ORM-моделей предметной области пока нет.
Корневой пакет `models/` из ПР3 и файлы `questions/models.py` и т. п. —
разные модули. Структура сохранённой консольной части описана ниже.

```text
GET /questions/1/
→ queryflow/urls.py: questions/, include("questions.urls")
→ questions/urls.py: <int:question_id>/, question_id=1
→ question_detail(request, question_id=1)
→ load_categories(), load_users(), load_questions()
→ get_question_by_id(), load_answers(), get_answers_for_question()
→ question.status_text() → page(title, content) → HttpResponse → браузер
```

Веб-слой повторно использует функции ПР3: загрузку, поиск, сортировку,
фильтрацию по категории и определение статусов. Для карточки ответа добавлена
`models.answers.get_answer_by_id()`. Обработчики GET не изменяют JSON.
Изменения из консоли видны при следующем запросе браузера.

HTML в ПР5 формируется строками в `views.py` через общую `page()`.
Данные из JSON экранируются через `html.escape()`. Ссылки строятся с помощью
`reverse()` по именам маршрутов. Bootstrap 5.3.3 подключён через CDN
(для его загрузки нужен интернет); собственный CSS встроен в `page()`.
Используются адаптивная сетка, карточки, списки, кнопки и бейджи Bootstrap.

## ПР5: проверка 404 и качества

По умолчанию `DEBUG=True`. При отсутствии объекта view явно возвращает
`HttpResponse(..., status=404)` в любом режиме. Общий обработчик неизвестного
URL объявлен в `queryflow/urls.py`; для его демонстрации отключить отладку:

```powershell
# Остановить текущий сервер:
$env:DJANGO_DEBUG = "False"
.\.venv\Scripts\python.exe manage.py runserver
# Открыть /nonexistent/, /questions/abc/, /questions/999/.
# После остановки вернуть обычный режим:
Remove-Item Env:DJANGO_DEBUG
```

`ALLOWED_HOSTS` разрешает `localhost`, `127.0.0.1`, `[::1]`.
Настройки предназначены для локальной учебной работы. Развёртывание на сервере
потребует отдельного `DJANGO_SECRET_KEY`, доменов и настройки статики.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m flake8 .
```

На момент выполнения ПР5 проходят 51 тест (23 теста ПР3 и 28 HTTP-проверок),
`check` и flake8 — без замечаний. Веб-тесты используют временные JSON-файлы
и проверяют данные, связи, статусы, экранирование, пустые списки, 404,
конвертеры URL, недопустимый Host и отсутствие записи при GET.
Вручную проверяются `/questions/1/`, `/categories/1/`, `/answers/1/`, ID `999`,
неизвестные пути, навигация и отображение на узком экране.

## ПР5: материалы для сдачи

- [Ответы на 25 пунктов таблицы оценивания](шпаргалка_пр5.md).
- [Отчёт ПР5](docs/ОТЧЁТ_ПР5_Коржов_С.С_ЭФБО-13-24.docx).
- [Репозиторий QueryFlow](https://github.com/pr1azzz/queryflow).

Коммиты работы имеют префикс `PR5:`. Публикация локальных коммитов выполняется
командой `git push` после проверки результата.

## Возможности сохранённой консольной версии

- просмотр и поиск категорий;
- публикация вопросов с проверкой длины текста и активности категории;
- поиск и фильтрация вопросов;
- добавление ответов;
- определение статуса вопроса (открыт / закрыт / ожидает ответа);
- закрытие вопроса;
- учёт пользователей;
- сохранение данных в JSON.

## Целевая аудитория

- студенты и преподаватели;
- участники учебных проектов и внутренних FAQ;
- администраторы категорий и статусов.

## Предметная область

Учёт вопросов и ответов (Q&A). Пользователи задают вопросы, относят их
к категориям и получают ответы.

## Основные классы

### Category — категория

Объект `Category` представляет тематическую группу вопросов.

Основные атрибуты:

- `id` — идентификатор;
- `name` — название;
- `is_active` — признак активности.

Основные методы:

- `is_available()` — доступна ли категория для публикации;
- `validate_name()` — проверка названия (`@staticmethod`);
- `__str__()` — строковое представление.

### User — пользователь

Объект `User` представляет автора вопроса или ответа.

Основные атрибуты:

- `id` — идентификатор;
- `name` — имя;
- `role` — роль (`user` / `moderator`).

Основные методы:

- `from_data()` — создание из словаря JSON (`@classmethod`);
- `__str__()` — строковое представление.

### Question — вопрос

Объект `Question` связывает категорию и автора.

Основные атрибуты:

- `id` — идентификатор;
- `text` — текст вопроса;
- `category` — объект `Category`;
- `author` — объект `User`;
- `is_closed` — признак закрытия;
- `created_on` — дата создания.

Основные методы:

- `close()` — закрыть вопрос;
- `status_text()` — текстовый статус с учётом числа ответов;
- `__str__()` — строковое представление.

### Answer — ответ

Объект `Answer` связывает вопрос и автора ответа.

Основные атрибуты:

- `id` — идентификатор;
- `text` — текст ответа;
- `question` — объект `Question`;
- `author` — объект `User`;
- `created_on` — дата создания.

Основные методы:

- `__str__()` — строковое представление.

## Взаимодействие объектов

```text
User ──создаёт──► Question ──относится к──► Category
User ──создаёт──► Answer   ──относится к──► Question
```

При работе приложения используются коллекции объектов:
`list[Category]`, `list[User]`, `list[Question]`, `list[Answer]`.
В JSON для связей хранятся идентификаторы (`category_id`, `author_id`,
`question_id`).

## Хранение данных

- `data/categories.json`
- `data/users.json`
- `data/questions.json`
- `data/answers.json`

При загрузке JSON преобразуется в объекты; при сохранении — обратно.

## Структура сохранённой консольной части (ПР3)

```text
queryflow/
├── README.md
├── requirements.txt
├── main.py
├── storage.py
├── utils.py
├── models/
│   ├── __init__.py
│   ├── categories.py
│   ├── users.py
│   ├── questions.py
│   └── answers.py
├── data/
│   ├── categories.json
│   ├── users.json
│   ├── questions.json
│   └── answers.json
└── tests/
    ├── test_categories.py
    ├── test_users.py
    ├── test_questions.py
    └── test_answers.py
```

## Назначение модулей

- `main.py` — точка входа, меню и пользовательские сценарии;
- `models/categories.py` — класс `Category` и функции коллекции;
- `models/users.py` — класс `User` и функции коллекции;
- `models/questions.py` — класс `Question` и функции коллекции;
- `models/answers.py` — класс `Answer` и функции коллекции;
- `storage.py` — загрузка/сохранение JSON ↔ объекты;
- `utils.py` — безопасный ввод;
- `tests/` — автоматизированные тесты.

## Требования

- Python 3.11+;
- Django 5.2;
- pytest;
- flake8.

Установка зависимостей:

```bash
pip install -r requirements.txt
```

## Запуск программы

```bash
python main.py
```

## Запуск тестов

```bash
.\.venv\Scripts\Activate.ps1
pytest -v
```

## Проверка качества кода

```bash
.\.venv\Scripts\Activate.ps1
flake8 . --exclude=.venv,venv,__pycache__,docs
```

## План развития

- ПР5 выполнена: Django, HTTP, URL, HTML/CSS/Bootstrap, JSON и объекты ПР3;
- следующие работы — шаблоны, контекст, наследование и Django ORM;
- ПР9–ПР11 — ORM, формы, регистрация и авторизация;
- REST API, Docker, CI/CD, расширенное тестирование.
