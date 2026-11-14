"""ПР11: формы фильтрации и публикации вопросов."""

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from categories.models import Category
from participants.models import User
from questions.models import Question
from queryflow.validators import not_future


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = "form-check-input"
            elif isinstance(widget, forms.Select):
                css = "form-select"
            else:
                css = "form-control"
            widget.attrs["class"] = css


class QuestionFilterForm(BootstrapFormMixin, forms.Form):
    q = forms.CharField(label="Текст вопроса", max_length=200, required=False)
    related = forms.CharField(label="Категория или автор (по имени)",
                              max_length=120, required=False)
    category = forms.ModelChoiceField(label="Категория", required=False,
                                      queryset=Category.objects.all())
    author = forms.ModelChoiceField(label="Автор", required=False,
                                    queryset=User.objects.all())
    date = forms.DateField(label="Дата публикации", required=False,
                           widget=forms.DateInput(attrs={"type": "date"}))
    since = forms.DateField(label="Опубликовано не раньше", required=False,
                            widget=forms.DateInput(attrs={"type": "date"}))
    status = forms.ChoiceField(label="Статус", required=False,
                               choices=[("", "Все"), *Question.Status.choices])
    sort = forms.ChoiceField(label="Порядок", required=False,
                             initial="newest", choices=[
                                 ("newest", "Сначала новые"),
                                 ("oldest", "Сначала старые"),
                                 ("category", "По категории"),
                                 ("author", "По автору")])
    page = forms.IntegerField(required=False, min_value=1, max_value=1000000,
                              widget=forms.HiddenInput)

    def clean(self):
        data = super().clean()
        if data.get("date") and data.get("since"):
            if data["date"] < data["since"]:
                raise ValidationError(
                    "Дата публикации должна быть не раньше начальной даты.")
        return data


class QuestionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "category", "author", "created_on"]
        labels = {"text": "Ваш вопрос"}
        help_texts = {"text": "Не менее 10 символов. Опишите задачу понятно."}
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 4, "placeholder": "Что вы хотите узнать?"}),
            "created_on": forms.DateInput(format="%Y-%m-%d",
                                          attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available = Q(is_active=True)
        if self.instance.pk:
            available |= Q(pk=self.instance.category_id)
        self.fields["category"].queryset = Category.objects.filter(available)
        self.fields["created_on"].validators.append(not_future)

    def clean_text(self):
        text = " ".join(self.cleaned_data["text"].split())
        if len(text) < 10:
            raise ValidationError(
                "Вопрос должен содержать не менее 10 символов.")
        return text

    def clean(self):
        data = super().clean()
        if all(data.get(key) for key in ("text", "category", "author")):
            duplicates = Question.objects.active().filter(
                text=data["text"], category=data["category"],
                author=data["author"]).exclude(pk=self.instance.pk)
            if (self.instance.status == Question.Status.OPEN
                    and duplicates.exists()):
                raise ValidationError(
                    "У автора уже есть такой открытый вопрос "
                    "в этой категории. "
                    "Отредактируйте или отзовите прежний вопрос.")
        return data
