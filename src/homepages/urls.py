from django.urls import path, register_converter

from . import views
from utils import converters

register_converter(converters.LanguageConverter, "language")

urlpatterns = [
    path("", views.homepages, name="homepages"),
    path("homepages/manage/", views.manage_homepages, name="manage_homepages"),
    path(
        "homepages/manage/<int:homepage_id>/<language:lang>/create/",
        views.create_homepage_translation,
        name="create_homepage_translation",
    ),
    path(
        "homepages/manage/<int:homepage_id>/<language:lang>/delete/",
        views.delete_homepage_translation,
        name="delete_homepage_translation",
    ),
    path(
        "homepages/manage/<int:homepage_id>/<language:lang>/restore/",
        views.restore_homepage_translation,
        name="restore_homepage_translation",
    ),
    path(
        "homepages/manage/<int:pk>/permissions/",
        views.manage_homepage_users,
        name="manage_homepage_users",
    ),
]
