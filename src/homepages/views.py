from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from .models import Homepage

User = get_user_model()


class HomepageUsersManageView(
    LoginRequiredMixin, UserPassesTestMixin, DetailView
):
    model = Homepage
    template_name = "homepages/manage_users.html"

    def test_func(self):
        homepage = self.get_object()
        is_attach = homepage.users.filter(id=self.request.user.id).exists()
        is_admin = self.request.user.is_superuser

        return is_attach or is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homepage = self.get_object()

        context["current_users"] = homepage.users.all()

        return context

    def post(self, request, *args, **kwargs):
        homepage = self.get_object()
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")

        if action and user_id:
            user = get_object_or_404(User, id=user_id)

            homepage.users.remove(user)

        return redirect("manage_homepage_users", pk=homepage.pk)


def homepages(request):
    return render(
        request,
        "home.html",
        {},
    )
