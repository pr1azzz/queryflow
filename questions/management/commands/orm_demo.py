"""Воспроизводимая демонстрация CRUD, без остаточных записей."""

from django.core.management.base import BaseCommand
from django.db import transaction

from categories.models import Category


class Command(BaseCommand):
    help = "Создать, прочитать, изменить, удалить тестовую категорию с откатом"

    @transaction.atomic
    def handle(self, *args, **options):
        category = Category.objects.create(name="Демонстрация ORM")
        pk = category.pk
        category.name = "Изменённое название"
        category.save(update_fields=["name"])
        self.stdout.write(Category.objects.get(pk=pk).name)
        category.delete()
        deleted = not Category.objects.filter(pk=pk).exists()
        self.stdout.write(f"Запись удалена: {deleted}")
        transaction.set_rollback(True)
