"""Одноразовый перенос ПР7 в ORM без перезаписи уже изменённых записей."""

import sqlite3
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from answers.models import Answer
from categories.models import Category
from participants.models import User
from questions.models import Question


class Command(BaseCommand):
    help = "Импорт SQLite ПР7 с сохранением ID и существующих записей ORM"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", type=Path,
            default=settings.BASE_DIR / "data/queryflow.sqlite")

    def handle(self, *args, **options):
        source = options["source"].resolve()
        try:
            with closing(sqlite3.connect(source.as_uri() + "?mode=ro",
                                         uri=True)) as connection:
                connection.row_factory = sqlite3.Row
                tables = {name: [dict(row) for row in connection.execute(
                    f"SELECT * FROM {name}")] for name in
                    ("categories", "users", "questions", "answers")}
            with transaction.atomic():
                models = [("categories", Category), ("users", User),
                          ("questions", Question), ("answers", Answer)]
                for table, model in models:
                    created = 0
                    for row in tables[table]:
                        pk = row.pop("id")
                        if table == "questions":
                            row["status"] = (Question.Status.CLOSED
                                             if row.pop("is_closed")
                                             else Question.Status.OPEN)
                        obj, is_new = model.objects.get_or_create(
                            pk=pk, defaults=row)
                        obj.full_clean()
                        created += is_new
                    self.stdout.write(f"{table}: добавлено {created}")
        except (sqlite3.Error, ValueError) as exc:
            raise CommandError(str(exc)) from exc
