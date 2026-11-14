# QueryFlow — система учёта вопросов и ответов

Индивидуальный проект №245 по дисциплине «Технологии разработки приложений
на базе фреймворков». Коржов Сергей Сергеевич, ЭФБО-13-24.
Текущий этап — ПР11: Django ORM, административная панель и веб-формы.

## Запуск (PowerShell, из корня проекта)

Python 3.11+, Django 5.2. Зависимости находятся в requirements.txt.

```powershell
# Если окружение ещё не создано:
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py import_legacy
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Сайт: <http://127.0.0.1:8000/>. При занятом порте можно указать
`python manage.py runserver 8011`. Остановка: Ctrl+C.
Bootstrap 5.3.3 подключён через CDN; для его загрузки нужен интернет.

## Данные и этапы проекта

- `db.sqlite3` — текущая база Django: служебные таблицы и четыре модели
  предметной области; создаётся миграциями и не включается в Git.
- `data/queryflow.sqlite` — сохранённая SQLite-база ПР7, источник импорта.
  SQL, модуль db/ и JSON сохранены для демонстрации предыдущих работ.
- `models/`, storage.py, main.py — прежнее консольное приложение с JSON.
  Оно работает независимо от новой веб-части.

`import_legacy` читает источник только для чтения, переносит данные одной
транзакцией, сохраняет ID и связи. Повторный запуск пропускает существующие
ID, поэтому изменения, сделанные в ORM, не перезаписываются. При ошибке
импорт откатывается целиком. Для переноса в уже заполненную посторонними
данными базу сначала нужно разрешить конфликты ID; команда предназначена
для первоначального переноса собственной базы ПР7.

Участники `participants.User` — авторы вопросов и ответов. Это отдельная
предметная модель, не учётные записи входа Django. ForeignKey использует
PROTECT: связанные категории, участников и вопросы нельзя удалить, пока
на них ссылаются другие записи.

## Страницы

| URL | Назначение |
| --- | --- |
| `/` | Главная |
| `/questions/` | Вопросы, фильтры, сортировка, пагинация |
| `/questions/open/` | Открытые вопросы |
| `/questions/unanswered/` | Открытые вопросы без ответов |
| `/questions/withdrawn/` | Отозванные вопросы |
| `/questions/search/` | Поиск |
| `/questions/statistics/` | Итоги, распределение по категориям и участникам |
| `/questions/<id>/` | Вопрос и ответы |
| `/questions/create/` | Создание вопроса |
| `/questions/<id>/edit/` | Редактирование вопроса |
| `/questions/<id>/cancel/` | Отзыв, только POST |
| `/questions/<id>/close/` | Закрытие открытого вопроса, только POST |
| `/answers/`, `/answers/<id>/` | Список и карточка ответа |
| `/answers/for/<question_id>/create/` | Ответ на выбранный вопрос |
| `/answers/<id>/edit/` | Редактирование ответа |
| `/categories/`, `/categories/active/` | Все и активные категории |
| `/categories/<id>/` | Старый адрес категории |
| `/categories/topic/<slug>/` | Основной адрес, get_absolute_url() |
| `/categories/<id>/edit/` | Изображение и свойства категории, для сотрудника |
| `/admin/` | Администрирование всех четырёх моделей |

Старые маршруты ПР5–ПР7 сохранены. Несуществующие объекты дают 404.
При DEBUG=True Django показывает техническую 404, при DEBUG=False — наш
шаблон. Для локальной проверки собственной 404 со статикой:
`$env:DJANGO_DEBUG="False"`, затем `python manage.py runserver --insecure`.
После проверки: `Remove-Item Env:DJANGO_DEBUG` и перезапуск сервера.

## Поиск и ORM (ПР9)

GET-параметры: q (текст), related (имя категории или автора), category,
author, date (точная дата), since (не раньше), status, sort, page.
Фильтры объединяются AND; поиск related использует OR по двум связанным
полям через Q. Значения sort разрешены словарём SORTS: newest, oldest,
category, author. Неизвестные значения дают 400. В SQLite icontains
игнорирует регистр ASCII, но учитывает регистр кириллицы; `%` и `_`
обрабатываются как буквальные символы пользовательского поиска.

Пагинация — Paginator, по 10 записей. Отрицательный или нечисловой page
даёт 400, положительный номер за пределами диапазона — последнюю страницу.
Тег querystring сохраняет фильтры и сортировку. Повторная отправка формы
фильтрации начинает выдачу с первой страницы.

В проекте больше 15 самостоятельных ORM-выражений, используемых интерфейсом:

| № | Выражение / сценарий | Где |
| --- | --- | --- |
| 1 | Category.objects.all(): каталог | categories/views.py |
| 2 | filter(is_active=True): активные категории | categories/views.py |
| 3 | get_object_or_404 по PK/slug | categories/views.py |
| 4 | category.questions.all(): обратная связь | categories/views.py |
| 5 | Question.objects.all(): общий список | questions/views.py |
| 6 | active(): открытые вопросы | questions/views.py |
| 7 | exclude статусов + answers__isnull: без ответов | questions/views.py |
| 8 | cancelled(): отозванные | questions/views.py |
| 9 | text__icontains: текстовый поиск | questions/queries.py |
| 10 | Q по category__name или author__name | questions/queries.py |
| 11 | category_id + author_id + дата: составной фильтр | questions/queries.py |
| 12 | order_by датой и PK: устойчивый порядок | questions/queries.py |
| 13 | order_by category__name: связанное поле | questions/queries.py |
| 14 | select_related(category, author) + Count: карточка | questions/views.py |
| 15 | question.answers.all(): ответы выбранного вопроса | questions/views.py |
| 16 | Answer.objects.all() + F + values: список ответов | questions/queries.py |
| 17 | Answer.select_related(question__category, author): карточка | answers/views.py |
| 18 | Question.aggregate с условными Count | questions/queries.py |
| 19 | Answer.aggregate с Count distinct авторов | questions/queries.py |
| 20 | Category.annotate(Count) + отбор групп | questions/queries.py |
| 21 | User.annotate(Count): участники, включая нулевые группы | questions/queries.py |
| 22 | User.objects.all(): список участников | questions/queries.py |
| 23 | Paginator: ограничение выборки страницей | questions/views.py |

Цепочка одного выражения не считается отдельным запросом на каждый метод.
Две формы получения связанных данных: values()+annotate(F()) для карточек
списка и select_related() для объектов подробной страницы.
`python manage.py orm_demo` показывает create/get/save/delete на тестовой
категории с откатом: после демонстрации лишних записей не остаётся.

## Админка и развитие модели (ПР10)

Для новой установки: `python manage.py createsuperuser`.
В подготовленном локальном окружении создан `queryflow_admin`; данные
входа находятся в игнорируемом файле `.env.local`. Пароль не включается в Git.

В admin.py настроены list_display, list_filter, search_fields, ordering,
list_per_page, autocomplete_fields и list_select_related. Inline-вопросы
доступны в карточках категорий и участников, inline-ответы — у вопроса.
Приложения, модели и поля имеют русские подписи.

Миграция questions/0002 сначала добавляет status, затем через RunPython
переносит is_closed=False → open, True → closed и удаляет старое поле.
Используются исторические модели apps.get_model(). Обратная миграция
сводит withdrawn к False: старый формат не имел отдельного отзыва.
QuestionQuerySet: active(), completed(), cancelled(), for_date().
Статистика отдельно учитывает OPEN, CLOSED, WITHDRAWN.

Адаптация проверки доступности: вопросы, ожидающие ответа на дату,
должны быть открыты и не иметь ответов. Закрытые и отозванные исключаются.
ПР11 дополняет правило проверкой одинакового открытого вопроса у автора.
Бронирования, помещения и их календарные ограничения в QueryFlow не вводятся.

Category.slug уникален; старые записи получают category-<id>. Новым
категориям по умолчанию назначается случайный уникальный slug; в админке
его можно заполнить по имени. GeneratedField Question.text_length вычисляет
Length(text) в SQLite, db_persist=True. После изменения исходного текста
для актуализации Python-объекта нужен refresh_from_db(). Общие название
сайта и количество активных категорий передаёт контекстный процессор.

При DEBUG=True с локального IP доступна свёрнутая Django Debug Toolbar.
Откройте её справа, затем SQL. Проверено: анонимный список без фильтров
выполняет 5 запросов — COUNT, страница карточек, общий счётчик и варианты
двух списков формы. Число запросов не растёт с количеством карточек.
Авторизация и дополнительные фильтры могут добавлять обоснованные запросы.
В карточке вопроса select_related загружает автора и категорию одним JOIN.

## Веб-формы (ПР11)

QuestionFilterForm — обычная Form; QuestionForm, AnswerForm, CategoryForm —
ModelForm. Обработка: привязка данных, is_valid(), cleaned_data, save(),
redirect (Post/Redirect/Get). Ошибки возвращаются с исходными значениями.
BootstrapFormMixin оформляет виджеты, общий шаблон показывает ошибки полей,
общие ошибки и подсказки. Все изменения выполняются через POST с CSRF;
GET на cancel/close возвращает 405, POST без токена — 403.

Правила предметной области:

- вопрос содержит минимум 10 символов; автор и категория существуют;
- одинаковый открытый вопрос одного автора в одной категории не создаётся
  повторно: exists()+exclude(pk=...) в форме и условный UniqueConstraint в БД;
- редактируемая запись не конфликтует сама с собой; отзыв освобождает
  возможность повторной публикации, сохраняя старую запись и ответы;
- дата публикации может быть в прошлом, но не в будущем; нельзя перенести
  дату вопроса позже имеющегося ответа или поставить ответ раньше вопроса;
- новые вопросы не создаются в архивной категории; существующий вопрос
  может сохранить прежнюю архивную категорию;
- ответы создаются и редактируются только у открытого вопроса;
- дата и существование связей проверяются формой и моделью; конфликт
  сохранения даёт ошибку формы, недоступность БД при сохранении — 503.

Это локальный учебный интерфейс: автора выбирают из списка участников.
Личный кабинет и проверка владельца вопроса не входят в ПР9–ПР11.
Изменение общих категорий и загрузка их изображений доступны сотруднику.

Category.image — ImageField с проверкой содержимого Pillow и лимитом 5 МБ.
Форма передаёт request.FILES, enctype=multipart/form-data. Файлы находятся
в media/categories/, в БД — относительный путь; MEDIA_URL формирует адрес.
При DEBUG=True Django раздаёт media локально. Изображение можно загрузить,
заменить или очистить через страницу категории и Django Admin. Если файла
нет, отображается текстовая заглушка. При замене старый файл автоматически
не удаляется. media/ не включается в Git.

## Проверки и материалы для защиты

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m flake8
```

Тесты используют отдельную БД и временные файлы. Проверяются старые
консольные сценарии и SQL ПР7, ORM, перенос и откат, миграция статуса,
админка, поиск, сортировка, пагинация, число запросов, формы, CSRF,
ошибки сохранения и изображения. Пароли тестовых пользователей применяются
только в изолированной тестовой БД.

В корне: шпаргалка_пр9.md (30 пунктов), шпаргалка_пр10.md (30 пунктов),
шпаргалка_пр11.md (20 пунктов). Отчёты DOCX находятся в родительском каталоге
рядом с отчётами ПР6–ПР7; сохранены их пять разделов и оформление.
Контрольные точки: ПР9 — ca17483, ПР10 — 147eea1; последующие коммиты
добавляют материалы для защиты и формы ПР11. Изменения локальные, без push.

Документация: [миграции Django](https://docs.djangoproject.com/en/5.2/topics/migrations/),
[ограничения моделей](https://docs.djangoproject.com/en/5.2/ref/models/constraints/),
[Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/stable/installation.html).
