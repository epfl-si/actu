from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Homepage


class HomepageUsersManageView(UserPassesTestMixin, DetailView):
    model = Homepage
    template_name = 'homepages/manage_users.html'

    def test_func(self):
        return self.request.user.is_staff


def homepages(request):

    return render(
        request,
        "home.html",
        {},
    )
