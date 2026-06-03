from django.shortcuts import render


def homepages(request):

    raise Exception("Make response code 500!")
    return render(
        request,
        "home.html",
        {},
    )
