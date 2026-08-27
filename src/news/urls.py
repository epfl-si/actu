from django.urls import path, register_converter

from utils import converters

from . import views

register_converter(converters.LanguageConverter, "language")

urlpatterns = [
    path("news/manage/", views.manage_news, name="manage_news"),
    path(
        "news/<language:lang>/create/",
        views.create_news,
        name="create_news",
    ),
    path(
        "news/<int:news_id>/<language:lang>/edit/",
        views.edit_news,
        name="edit_news",
    ),
    path(
        "news/manage/<int:news_id>/<language:lang>/delete/",
        views.delete_news_translation,
        name="delete_news_translation",
    ),
    path(
        "news/manage/<int:news_id>/<language:lang>/restore/",
        views.restore_news_translation,
        name="restore_news_translation",
    ),
]
