from django.contrib import admin

from participants.models import User
from categories.admin import QuestionInline


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "role"]
    list_filter = ["role"]
    search_fields = ["name"]
    ordering = ["name", "pk"]
    list_per_page = 20
    inlines = [QuestionInline]
