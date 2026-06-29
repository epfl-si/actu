from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from utils.accred_client import AccredServiceClient

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
        is_admin = self.request.user.is_staff
        return is_attach or is_admin

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        is_ajax = (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
        )

        if is_ajax:
            query = request.GET.get("q", "").strip()
            data = []

            if query:
                client = AccredServiceClient()

                external_results = client.search_persons_by_right(query)

                attached_scipers = [
                    str(s)
                    for s in self.object.users.values_list("sciper", flat=True)
                ]

                for user_data in external_results:
                    if str(user_data["sciper"]) not in attached_scipers:
                        data.append(
                            {
                                "sciper": user_data["sciper"],
                                "text": user_data["displayName"],
                                "first_name": user_data.get("first_name", ""),
                                "last_name": user_data.get("last_name", ""),
                            }
                        )

            return JsonResponse({"results": data})

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_users"] = self.get_object().users.all()
        return context

    def post(self, request, *args, **kwargs):
        homepage = self.get_object()
        action = request.POST.get("action")

        if action == "add":
            sciper = request.POST.get("sciper")
            if sciper:
                user = User.objects.filter(sciper=sciper).first()

                if not user:
                    client = AccredServiceClient()
                    person_details = client.get_person_details(sciper)

                    if person_details:
                        user = User.objects.create(
                            sciper=person_details["sciper"],
                            username=person_details["username"],
                            first_name=person_details["first_name"],
                            last_name=person_details["last_name"],
                            email=person_details["email"],
                        )

                if user:
                    homepage.users.add(user)

        elif action == "remove":
            user_id = request.POST.get("user_id")
            if user_id:
                user = get_object_or_404(User, id=user_id)
                homepage.users.remove(user)

        return redirect("manage_homepage_users", pk=homepage.pk)


def homepages(request):
    return render(
        request,
        "home.html",
        {},
    )
