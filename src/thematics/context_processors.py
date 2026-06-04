from .models import Thematic

def global_thematics(request):
    try:
        active_thematics = Thematic.objects.filter(is_active=True).order_by('order')
    except Exception:
        active_thematics = []

    return {
        "thematics": active_thematics
    }
