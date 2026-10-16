from django.urls import path

from . import views

app_name = "answers"
urlpatterns = [
    path("", views.answers, name="list"),
    path("<int:answer_id>/", views.answer_detail, name="detail"),
]
