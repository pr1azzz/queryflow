from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Length
from django.urls import reverse
from django.utils import timezone

from queryflow.validators import not_future


class QuestionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Question.Status.OPEN)

    def cancelled(self):
        return self.filter(status=Question.Status.WITHDRAWN)

    def completed(self):
        return self.filter(status=Question.Status.CLOSED)

    def for_date(self, day):
        return self.filter(created_on=day)


class Question(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"
        WITHDRAWN = "withdrawn", "Отозван"

    text = models.TextField("Текст вопроса", max_length=2000)
    category = models.ForeignKey(
        "categories.Category", on_delete=models.PROTECT,
        related_name="questions", verbose_name="Категория")
    author = models.ForeignKey(
        "participants.User", on_delete=models.PROTECT,
        related_name="questions", verbose_name="Автор")
    status = models.CharField("Статус", max_length=12, choices=Status,
                              default=Status.OPEN)
    text_length = models.GeneratedField(
        expression=Length("text"), output_field=models.IntegerField(),
        db_persist=True, verbose_name="Символов в вопросе")
    objects = QuestionQuerySet.as_manager()

    created_on = models.DateField(
        "Дата публикации", default=timezone.localdate, validators=[not_future])

    class Meta:
        ordering = ["-created_on", "-pk"]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        constraints = [models.CheckConstraint(
            condition=models.Q(status__in=["open", "closed", "withdrawn"]),
            name="question_valid_status"), models.UniqueConstraint(
                fields=["text", "category", "author"],
                condition=models.Q(status="open"),
                name="unique_open_question_per_author")]

    def __str__(self):
        return self.text[:80]

    def get_absolute_url(self):
        return reverse("questions:detail", args=[self.pk])

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    def cancel(self):
        self.status = self.Status.WITHDRAWN
        self.save(update_fields=["status"])

    def clean(self):
        super().clean()
        if self.category_id and not self.category.is_active:
            previous = type(self).objects.filter(pk=self.pk).first()
            if previous is None or previous.category_id != self.category_id:
                raise ValidationError({"category": "Категория в архиве."})
        if self.pk and self.created_on:
            if self.answers.filter(created_on__lt=self.created_on).exists():
                raise ValidationError({
                    "created_on": "Дата вопроса не может быть позже ответа."})
