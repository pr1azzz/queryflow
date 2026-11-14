from django.urls import path

from . import views

app_name = "answers"
urlpatterns = [
    path("for/<int:question_id>/create/", views.answer_create, name="create"),
    path("<int:answer_id>/edit/", views.answer_edit, name="edit"),
    path("", views.answers, name="list"),
    path("<int:answer_id>/", views.answer_detail, name="detail"),
]
