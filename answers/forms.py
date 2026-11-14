from django import forms
from django.core.exceptions import ValidationError

from answers.models import Answer
from questions.forms import BootstrapFormMixin
from queryflow.validators import not_future


class AnswerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text", "author", "created_on"]
        labels = {"text": "Ваш ответ"}
        widgets = {
            "text": forms.Textarea(attrs={"rows": 5}),
            "created_on": forms.DateInput(format="%Y-%m-%d",
                                          attrs={"type": "date"}),
        }
        help_texts = {"text": "Ответ будет связан с открытым вопросом."}

    def __init__(self, *args, question, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.question = question
        self.fields["created_on"].validators.append(not_future)

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if len(text) < 3:
            raise ValidationError(
                "Ответ должен содержать не менее 3 символов.")
        return text
