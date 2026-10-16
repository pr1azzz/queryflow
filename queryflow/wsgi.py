"""Точка входа WSGI-сервера."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queryflow.settings")
application = get_wsgi_application()
