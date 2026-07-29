from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from utils.accred_client import AccredServiceClient

from .models import Homepage

User = get_user_model()


def _handle_post_action(request, homepage):
    action = request.POST.get("action")

    if action == "add":
        sciper = request.POST.get("sciper")
        if not sciper:
            return

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


def _get_ajax_search_results(request, homepage):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    client = AccredServiceClient()
    external_results = client.search_persons_by_right(query)

    attached_scipers = {
        str(s) for s in homepage.users.values_list("sciper", flat=True)
    }
    data = []

    for user_data in external_results:
        if str(user_data["sciper"]) not in attached_scipers:
            data.append(
                {
                    "sciper": user_data["sciper"],
                    "text": user_data["display_name"],
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                }
            )

    return JsonResponse({"results": data})


@login_required
def manage_homepage_users(request, pk):
    homepage = get_object_or_404(Homepage, pk=pk)

    is_attach = homepage.users.filter(id=request.user.id).exists()
    is_admin = request.user.is_staff
    if not (is_attach or is_admin):
        raise PermissionDenied

    if request.method == "POST":
        _handle_post_action(request, homepage)
        return redirect("manage_homepage_users", pk=homepage.pk)

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
    )
    if is_ajax:
        return _get_ajax_search_results(request, homepage)

    context = {
        "homepage": homepage,
        "current_users": homepage.users.all(),
    }
    return render(request, "homepages/manage_users.html", context)


def homepages(request):
    return render(request, "home.html", {})
