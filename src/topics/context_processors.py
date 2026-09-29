from .models import Topic


def global_topics(request):
    qs = Topic.objects.filter(is_active=True).order_by("order")

    main_topics = [t for t in qs if t.is_main]

    other_topics = sorted(
        [t for t in qs if not t.is_main], key=lambda t: str(t).lower()
    )

    return {
        "main_topics": main_topics,
        "other_topics": other_topics,
    }
