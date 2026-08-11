from django.urls import path

from . import views

urlpatterns = [
    path(
        "news/create/",
        views.create_news,
        name="create_news",
    ),
    path(
        "news/<int:news_id>/edit/",
        views.edit_news,
        name="edit_news",
    ),
]
