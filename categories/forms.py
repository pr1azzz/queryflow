from django import forms

from categories.models import Category
from questions.forms import BootstrapFormMixin


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "is_active", "image"]
        help_texts = {"image": "PNG, JPEG или другое изображение, до 5 МБ."}
