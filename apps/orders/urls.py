from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.crear, name="crear"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/items/agregar/", views.agregar_item, name="agregar-item"),
    path("<int:pk>/items/<int:item_pk>/eliminar/", views.eliminar_item, name="eliminar-item"),
    path("<int:pk>/estado/", views.cambiar_estado, name="cambiar-estado"),
    path("<int:pk>/comanda/", views.comanda, name="comanda"),
]
