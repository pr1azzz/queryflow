from django.urls import path

from . import views

app_name = "questions"
urlpatterns = [
    path("", views.questions, name="list"),
    path("open/", views.open_questions, name="open"),
    path("unanswered/", views.unanswered_questions, name="unanswered"),
    path("search/", views.search, name="search"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:question_id>/", views.question_detail, name="detail"),
]
