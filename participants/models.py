"""Участник предметной области; учётные записи входа — django.contrib.auth."""

from django.db import models


class User(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Участник"
        MODERATOR = "moderator", "Модератор"

    name = models.CharField("Имя", max_length=120)
    role = models.CharField("Роль", max_length=20, choices=Role,
                            default=Role.USER)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self):
        return self.name
