from django.shortcuts import render


def homepages(request):

    return render(
        request,
        "home.html",
        {},
    )
