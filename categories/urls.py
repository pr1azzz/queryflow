from django.urls import path

from . import views

app_name = "categories"
urlpatterns = [
    path("<int:category_id>/edit/", views.category_edit, name="edit"),
    path("topic/<slug:slug>/", views.category_detail, name="by_slug"),
    path("", views.categories, name="list"),
    path("active/", views.active_categories, name="active"),
    path("<int:category_id>/", views.category_detail, name="detail"),
]
