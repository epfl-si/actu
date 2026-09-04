from django.urls import path

from . import views

urlpatterns = [
    path("news/", views.list_news, name="list_news"),
    path("news/manage/", views.manage_news, name="manage_news"),
    path(
        "news/manage/<int:news_id>/<str:lang>/delete/",
        views.delete_news_translation,
        name="delete_news_translation",
    ),
    path(
        "news/manage/<int:news_id>/<str:lang>/restore/",
        views.restore_news_translation,
        name="restore_news_translation",
    ),
]
