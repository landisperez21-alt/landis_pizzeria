from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("cuentas/", include("apps.accounts.urls")),
    path("carta/", include("apps.catalog.urls")),
    path("clientes/", include("apps.customers.urls")),
    path("pedidos/", include("apps.orders.urls")),
    path("pagos/", include("apps.payments.urls")),
    path("inventario/", include("apps.inventory.urls")),
]

handler403 = core_views.error_403
handler404 = core_views.error_404
handler500 = core_views.error_500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
