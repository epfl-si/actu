from django.urls import path

from .views import homepages

urlpatterns = [
    path("", homepages, name="homepages"),
]
