from django.urls import path

from .views import HomepageUsersManageView, homepages

urlpatterns = [
    path("", homepages, name="homepages"),
    path(
        "homepages/manage/<int:pk>/permissions/",
        HomepageUsersManageView.as_view(),
        name="manage_homepage_users",
    ),
]
