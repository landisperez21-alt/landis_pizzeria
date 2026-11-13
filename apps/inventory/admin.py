from django.contrib import admin

from .models import Insumo, MovimientoInsumo


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "unidad", "stock", "stock_minimo", "costo_unitario", "activo")
    list_filter = ("unidad", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(MovimientoInsumo)
class MovimientoInsumoAdmin(admin.ModelAdmin):
    list_display = ("insumo", "tipo", "cantidad", "usuario", "creado_en")
    list_filter = ("tipo", "creado_en")
    search_fields = ("insumo__nombre", "motivo")
