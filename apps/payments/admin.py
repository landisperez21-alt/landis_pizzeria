from django.contrib import admin

from .models import MetodoPago, Pago, SesionCaja


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_editable = ("activo",)


@admin.register(SesionCaja)
class SesionCajaAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "fecha_apertura", "monto_inicial", "fecha_cierre", "monto_final")
    list_filter = ("fecha_apertura",)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "metodo", "monto", "estado", "fecha_pago", "usuario")
    list_filter = ("estado", "metodo", "fecha_pago")
    search_fields = ("pedido__codigo", "referencia_operacion")
