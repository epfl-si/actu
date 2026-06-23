from django.urls import path

from .views import HomepageUsersManageView, homepages

urlpatterns = [
    path("", homepages, name="homepages"),
    path(
        "admin/homepage/<int:pk>/manage/",
        HomepageUsersManageView.as_view(),
        name="manage_homepage_users",
    ),
]
