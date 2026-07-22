from entities.models import Entity


def footer_entities(request):
    entities = Entity.objects.filter(is_active=True, is_main=True).order_by(
        "order"
    )
    return {"footer_entities": entities}
