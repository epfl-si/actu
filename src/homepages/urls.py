from django.urls import path

from .views import homepages, manage_homepage_users

urlpatterns = [
    path("", homepages, name="homepages"),
    path(
        "homepages/manage/<int:pk>/permissions/",
        manage_homepage_users,
        name="manage_homepage_users",
    ),
]
