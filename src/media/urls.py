from django.urls import path

from . import views

urlpatterns = [
    path(
        "news/<int:news_id>/media/upload/",
        views.upload_news_images,
        name="upload_news_images",
    ),
    path(
        "news/<int:news_id>/media/<int:image_id>/edit/",
        views.edit_news_image,
        name="edit_news_image",
    ),
    path(
        "news/<int:news_id>/media/<int:image_id>/delete/",
        views.delete_news_image,
        name="delete_news_image",
    ),
]
