from .models import Thematic


def global_thematics(request):
    qs = Thematic.objects.filter(is_active=True).order_by("order")

    main_thematics = [t for t in qs if t.is_main]

    other_thematics = sorted(
        [t for t in qs if not t.is_main], key=lambda t: str(t).lower()
    )

    return {
        "main_thematics": main_thematics,
        "other_thematics": other_thematics,
    }
