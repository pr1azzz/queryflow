from django.db import models
from django.urls import reverse
from django.utils import timezone


class Question(models.Model):
    text = models.TextField("Текст вопроса", max_length=2000)
    category = models.ForeignKey(
        "categories.Category", on_delete=models.PROTECT,
        related_name="questions", verbose_name="Категория")
    author = models.ForeignKey(
        "participants.User", on_delete=models.PROTECT,
        related_name="questions", verbose_name="Автор")
    is_closed = models.BooleanField("Закрыт", default=False)
    created_on = models.DateField(
        "Дата публикации", default=timezone.localdate)

    class Meta:
        ordering = ["-created_on", "-pk"]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text[:80]

    def get_absolute_url(self):
        return reverse("questions:detail", args=[self.pk])
