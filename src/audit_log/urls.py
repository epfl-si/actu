from django.urls import path

from . import views

urlpatterns = [
    path("history/", views.global_history_view, name="global_history"),
]
