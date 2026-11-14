from django.contrib import admin

from answers.models import Answer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "question", "author", "created_on"]
    list_filter = ["created_on", "question__category"]
    search_fields = ["text", "question__text", "author__name"]
    ordering = ["-created_on", "-pk"]
    list_per_page = 20
    list_select_related = ["question", "author"]
    autocomplete_fields = ["question", "author"]
