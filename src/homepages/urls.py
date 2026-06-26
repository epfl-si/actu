from django.urls import path

from . import views

urlpatterns = [
    path("", views.homepages, name="homepages"),
    path("homepages/manage/", views.manage_homepages, name="manage_homepages"),
]
