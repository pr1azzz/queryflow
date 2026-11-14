from django.contrib import admin

from categories.models import Category
from questions.models import Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ["text", "author", "status", "created_on"]
    autocomplete_fields = ["author"]
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    ordering = ["name", "pk"]
    list_per_page = 20
    prepopulated_fields = {"slug": ("name",)}
    inlines = [QuestionInline]
