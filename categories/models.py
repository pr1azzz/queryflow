from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("Название", max_length=120)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("categories:detail", args=[self.pk])
