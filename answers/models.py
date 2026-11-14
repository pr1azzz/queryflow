from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from queryflow.validators import not_future


class Answer(models.Model):
    text = models.TextField("Текст ответа", max_length=5000)
    question = models.ForeignKey(
        "questions.Question", on_delete=models.PROTECT,
        related_name="answers", verbose_name="Вопрос")
    author = models.ForeignKey(
        "participants.User", on_delete=models.PROTECT,
        related_name="answers", verbose_name="Автор")
    created_on = models.DateField(
        "Дата публикации", default=timezone.localdate, validators=[not_future])

    class Meta:
        ordering = ["created_on", "pk"]
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.text[:80]

    def get_absolute_url(self):
        return reverse("answers:detail", args=[self.pk])

    def clean(self):
        super().clean()
        if self.question_id:
            if self.question.status != self.question.Status.OPEN:
                raise ValidationError(
                    "Ответы доступны только для открытых вопросов.")
            if self.created_on and self.created_on < self.question.created_on:
                raise ValidationError({
                    "created_on": ("Ответ не может быть опубликован "
                                   "раньше вопроса.")})
