from django.urls import path

from . import views

urlpatterns = [
    path("", views.homepages, name="homepages"),
    path("homepages/manage/", views.manage_homepages, name="manage_homepages"),
    path(
        "homepages/manage/<int:homepage_id>/<str:lang>/create/",
        views.create_homepage_translation,
        name="create_homepage_translation",
    ),
    path(
        "homepages/manage/<int:homepage_id>/<str:lang>/delete/",
        views.delete_homepage_translation,
        name="delete_homepage_translation",
    ),
    path(
        "homepages/manage/<int:homepage_id>/<str:lang>/restore/",
        views.restore_homepage_translation,
        name="restore_homepage_translation",
    ),
]
