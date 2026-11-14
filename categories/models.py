from uuid import uuid4

from django.db import models
from django.urls import reverse


def category_slug():
    return uuid4().hex


class Category(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Адрес", unique=True, default=category_slug)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("categories:by_slug", args=[self.slug])
