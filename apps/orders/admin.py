from django.contrib import admin

from .models import DetalleExtra, DetallePedido, Pedido


class DetalleExtraInline(admin.TabularInline):
    model = DetalleExtra
    extra = 0


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "cliente", "tipo", "estado", "total", "creado_en")
    list_filter = ("tipo", "estado", "creado_en")
    search_fields = ("codigo", "cliente__nombre")
    inlines = [DetallePedidoInline]
    readonly_fields = ("codigo", "creado_en", "actualizado_en")
