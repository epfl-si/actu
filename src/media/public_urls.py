from django.urls import path

from . import views

urlpatterns = [
    path(
        "image/<int:image_id>/<image_resolution:resolution>.jpg",
        views.serve_news_image,
        name="serve_news_image",
    ),
]
