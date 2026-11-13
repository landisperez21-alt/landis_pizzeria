from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.crear, name="crear"),
    path("<int:pk>/anular/", views.anular, name="anular"),
    path("caja/", views.caja, name="caja"),
    path("caja/abrir/", views.abrir_caja, name="abrir"),
    path("caja/<int:pk>/cerrar/", views.cerrar_caja, name="cerrar"),
]
