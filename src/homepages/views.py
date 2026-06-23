from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import DetailView

from .models import Homepage

User = get_user_model()


class HomepageUsersManageView(UserPassesTestMixin, DetailView):
    model = Homepage
    template_name = "homepages/manage_users.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homepage = self.get_object()

        context["current_users"] = homepage.users.all()

        return context


def homepages(request):
    return render(
        request,
        "home.html",
        {},
    )
