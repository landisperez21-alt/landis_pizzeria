from django.contrib import admin

from .models import Categoria, ComboItem, Ingrediente, Producto, RecetaItem, Tamano


class RecetaItemInline(admin.TabularInline):
    model = RecetaItem
    extra = 0


class ComboItemInline(admin.TabularInline):
    model = ComboItem
    fk_name = "combo"
    extra = 0


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "activo")
    list_editable = ("orden", "activo")


@admin.register(Tamano)
class TamanoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "porciones", "factor_precio", "activo")


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_extra", "activo")
    list_editable = ("precio_extra", "activo")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "tipo", "precio_base", "destacado", "activo")
    list_filter = ("tipo", "categoria", "activo", "destacado")
    search_fields = ("nombre", "descripcion")
    inlines = [RecetaItemInline, ComboItemInline]
