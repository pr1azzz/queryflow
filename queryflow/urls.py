"""Корневые маршруты: передают остаток URL приложениям."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("questions/", include("questions.urls")),
    path("categories/", include("categories.urls")),
    path("answers/", include("answers.urls")),
]

handler404 = "homepage.views.page_not_found"

from django.conf import settings  # noqa: E402

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
