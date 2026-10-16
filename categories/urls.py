from django.urls import path

from . import views

app_name = "categories"
urlpatterns = [
    path("", views.categories, name="list"),
    path("<int:category_id>/", views.category_detail, name="detail"),
]
