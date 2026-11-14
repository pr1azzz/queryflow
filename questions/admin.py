from django.contrib import admin

from answers.models import Answer
from questions.models import Question


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    autocomplete_fields = ["author"]
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "category", "author", "status",
                    "created_on", "text_length"]
    list_filter = ["status", "category", "created_on"]
    search_fields = ["text", "category__name", "author__name"]
    ordering = ["-created_on", "-pk"]
    list_per_page = 20
    list_select_related = ["category", "author"]
    autocomplete_fields = ["category", "author"]
    readonly_fields = ["text_length"]
    date_hierarchy = "created_on"
    inlines = [AnswerInline]
