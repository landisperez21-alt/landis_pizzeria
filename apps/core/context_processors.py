from django.conf import settings


def branding(request):
    """Expone la configuracion de marca a todas las plantillas."""
    return {"BRAND": settings.BRAND}
