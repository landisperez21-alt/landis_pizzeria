from django.urls import path

from apps.core.crud import CrudConfig

from .forms import CategoriaForm, IngredienteForm, ProductoForm, TamanoForm
from .models import Categoria, Ingrediente, Producto, Tamano

app_name = "catalog"

categorias = CrudConfig(
    Categoria, CategoriaForm, "Categorias", "catalog:categorias", singular="Categoria",
    columnas=[
        {"label": "Categoria", "campo": "nombre"},
        {"label": "Descripcion", "campo": "descripcion"},
        {"label": "Orden", "campo": "orden"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("nombre", "descripcion"),
    orden=("orden", "nombre"),
    roles=("admin",),
)

tamanos = CrudConfig(
    Tamano, TamanoForm, "Tamanos", "catalog:tamanos", singular="Tamano",
    columnas=[
        {"label": "Tamano", "campo": "nombre"},
        {"label": "Porciones", "campo": "porciones"},
        {"label": "Factor de precio", "campo": "factor_precio", "tipo": "numero"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    orden=("factor_precio",),
    roles=("admin",),
)

ingredientes = CrudConfig(
    Ingrediente, IngredienteForm, "Ingredientes extra", "catalog:ingredientes", singular="Ingrediente",
    columnas=[
        {"label": "Ingrediente", "campo": "nombre"},
        {"label": "Precio extra", "campo": "precio_extra", "tipo": "moneda"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("nombre",),
    roles=("admin",),
)

productos = CrudConfig(
    Producto, ProductoForm, "Productos de la carta", "catalog:productos", singular="Producto",
    columnas=[
        {"label": "Producto", "campo": "nombre"},
        {"label": "Categoria", "campo": "categoria.nombre"},
        {"label": "Tipo", "campo": "get_tipo_display"},
        {"label": "Precio base", "campo": "precio_base", "tipo": "moneda"},
        {"label": "Destacado", "campo": "destacado", "tipo": "bool", "texto_true": "Si", "texto_false": "No"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("nombre", "descripcion"),
    orden=("categoria__orden", "nombre"),
    roles=("admin", "cajero"),
)

urlpatterns = [
    path("categorias/", categorias.lista, name="categorias"),
    path("categorias/nueva/", categorias.crear, name="categorias-crear"),
    path("categorias/<int:pk>/editar/", categorias.editar, name="categorias-editar"),
    path("categorias/<int:pk>/alternar/", categorias.alternar, name="categorias-alternar"),

    path("tamanos/", tamanos.lista, name="tamanos"),
    path("tamanos/nuevo/", tamanos.crear, name="tamanos-crear"),
    path("tamanos/<int:pk>/editar/", tamanos.editar, name="tamanos-editar"),
    path("tamanos/<int:pk>/alternar/", tamanos.alternar, name="tamanos-alternar"),

    path("ingredientes/", ingredientes.lista, name="ingredientes"),
    path("ingredientes/nuevo/", ingredientes.crear, name="ingredientes-crear"),
    path("ingredientes/<int:pk>/editar/", ingredientes.editar, name="ingredientes-editar"),
    path("ingredientes/<int:pk>/alternar/", ingredientes.alternar, name="ingredientes-alternar"),

    path("productos/", productos.lista, name="productos"),
    path("productos/nuevo/", productos.crear, name="productos-crear"),
    path("productos/<int:pk>/editar/", productos.editar, name="productos-editar"),
    path("productos/<int:pk>/alternar/", productos.alternar, name="productos-alternar"),
]
