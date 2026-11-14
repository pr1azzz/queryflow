from django.core.exceptions import ValidationError
from django.utils import timezone


def not_future(value):
    if value > timezone.localdate():
        raise ValidationError("Дата публикации не может быть в будущем.")


def validate_image_size(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("Размер изображения не должен превышать 5 МБ.")
