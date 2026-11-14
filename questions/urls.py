from django.urls import path

from . import views

app_name = "questions"
urlpatterns = [
    path("create/", views.question_create, name="create"),
    path("<int:question_id>/edit/", views.question_edit, name="edit"),
    path("<int:question_id>/cancel/", views.question_cancel, name="cancel"),
    path("<int:question_id>/close/", views.question_close, name="close"),
    path("withdrawn/", views.withdrawn_questions, name="withdrawn"),
    path("", views.questions, name="list"),
    path("open/", views.open_questions, name="open"),
    path("unanswered/", views.unanswered_questions, name="unanswered"),
    path("search/", views.search, name="search"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:question_id>/", views.question_detail, name="detail"),
]
