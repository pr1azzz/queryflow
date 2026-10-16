from django.urls import path

from . import views

app_name = "questions"
urlpatterns = [
    path("", views.questions, name="list"),
    path("<int:question_id>/", views.question_detail, name="detail"),
]
