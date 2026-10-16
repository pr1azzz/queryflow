"""Главная страница, общий HTML-каркас и обработчик ошибки 404."""

from html import escape

from django.http import HttpResponse
from django.urls import reverse


def page(title, content):
    """Собрать HTML; content — готовая разметка с экранированными данными."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    home_url = reverse("homepage:index")
    questions_url = reverse("questions:list")
    categories_url = reverse("categories:list")
    answers_url = reverse("answers:list")
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)} | QueryFlow</title>
    <link rel="stylesheet" href="{bootstrap}">
    <style>
        body {{ background: #f5f7fb; color: #223047; }}
        main {{ min-height: 70vh; overflow-wrap: anywhere; }}
        .brand {{ font-weight: 800; letter-spacing: -.04em; }}
        .hero {{ border-left: 5px solid #0d6efd; }}
        .card {{ border: 1px solid #e1e7f0; border-radius: 1rem; }}
        .preserve-lines {{ white-space: pre-wrap; }}
        .nav-link {{ font-weight: 500; }}
        a:focus-visible {{ outline: 3px solid #0d6efd; }}
    </style>
</head>
<body>
    <header class="bg-white border-bottom">
        <nav class="container py-3 d-flex flex-wrap align-items-center gap-3"
             aria-label="Основная навигация">
            <a class="brand fs-3 text-decoration-none me-auto"
               href="{home_url}">QueryFlow<span class="text-dark">.</span></a>
            <div class="nav flex-wrap">
                <a class="nav-link" href="{home_url}">Главная</a>
                <a class="nav-link" href="{questions_url}">Вопросы</a>
                <a class="nav-link" href="{categories_url}">Категории</a>
                <a class="nav-link" href="{answers_url}">Ответы</a>
            </div>
        </nav>
    </header>
    <main class="container py-5">{content}</main>
    <footer class="container py-4 border-top text-secondary small">
        QueryFlow · Система учёта вопросов и ответов
    </footer>
</body>
</html>"""


def index(request):
    """Представить проект и дать ссылки на основные разделы."""
    questions_url = reverse("questions:list")
    categories_url = reverse("categories:list")
    answers_url = reverse("answers:list")
    content = f"""
    <section class="hero bg-white rounded-4 p-4 p-md-5 mb-4">
        <p class="text-primary fw-semibold">ВОПРОСЫ. ОТВЕТЫ. ЗНАНИЯ.</p>
        <h1 class="display-4 fw-bold">Знания начинаются с вопроса</h1>
        <p class="lead text-secondary mt-3">
            QueryFlow помогает находить вопросы по темам,
            читать ответы и следить за ходом обсуждений.
        </p>
        <a href="{questions_url}" class="btn btn-primary btn-lg mt-2">
            Перейти к вопросам →
        </a>
    </section>
    <div class="row g-4">
        <section class="col-md-4">
            <div class="card h-100"><div class="card-body p-4">
                <h2 class="h4">Вопросы</h2>
                <p>Тексты обсуждений, авторы и статусы решения.</p>
                <a href="{questions_url}">Смотреть вопросы →</a>
            </div></div>
        </section>
        <section class="col-md-4">
            <div class="card h-100"><div class="card-body p-4">
                <h2 class="h4">Категории</h2>
                <p>Темы для поиска информации и связанных вопросов.</p>
                <a href="{categories_url}">Выбрать тему →</a>
            </div></div>
        </section>
        <section class="col-md-4">
            <div class="card h-100"><div class="card-body p-4">
                <h2 class="h4">Ответы</h2>
                <p>Объяснения участников и ссылки на обсуждения.</p>
                <a href="{answers_url}">Читать ответы →</a>
            </div></div>
        </section>
    </div>
    """
    return HttpResponse(page("Главная", content))


def page_not_found(request, exception):
    """Обработать неизвестный маршрут при DEBUG=False."""
    home_url = reverse("homepage:index")
    content = f"""
    <section class="card"><div class="card-body p-5">
        <p class="display-3 text-primary fw-bold">404</p>
        <h1>Страница не найдена</h1>
        <p>Проверьте адрес или вернитесь на главную страницу.</p>
        <a href="{home_url}" class="btn btn-primary">На главную</a>
    </div></section>
    """
    return HttpResponse(page("Страница не найдена", content), status=404)
