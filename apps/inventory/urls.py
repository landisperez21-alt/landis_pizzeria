from django.urls import path

from apps.core.crud import CrudConfig

from . import views
from .forms import InsumoForm
from .models import Insumo

app_name = "inventory"

insumos = CrudConfig(
    Insumo, InsumoForm, "Insumos", "inventory:insumos", singular="Insumo",
    columnas=[
        {"label": "Codigo", "campo": "codigo"},
        {"label": "Insumo", "campo": "nombre"},
        {"label": "Unidad", "campo": "get_unidad_display"},
        {"label": "Stock", "campo": "stock", "tipo": "numero"},
        {"label": "Minimo", "campo": "stock_minimo", "tipo": "numero"},
        {"label": "Costo", "campo": "costo_unitario", "tipo": "moneda"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("codigo", "nombre"),
    roles=("admin", "cocinero"),
)

urlpatterns = [
    path("insumos/", insumos.lista, name="insumos"),
    path("insumos/nuevo/", insumos.crear, name="insumos-crear"),
    path("insumos/<int:pk>/editar/", insumos.editar, name="insumos-editar"),
    path("insumos/<int:pk>/alternar/", insumos.alternar, name="insumos-alternar"),

    path("movimientos/", views.movimientos, name="movimientos"),
    path("movimientos/registrar/", views.registrar_movimiento, name="movimientos-registrar"),
]
