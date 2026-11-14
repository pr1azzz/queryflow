from uuid import uuid4

from django.db import models
from django.urls import reverse

from queryflow.validators import validate_image_size


def category_slug():
    return uuid4().hex


class Category(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Адрес", unique=True, default=category_slug)
    image = models.ImageField("Изображение", upload_to="categories/%Y/%m/",
                              blank=True, validators=[validate_image_size])
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("categories:by_slug", args=[self.slug])
