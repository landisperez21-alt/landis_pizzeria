from django.contrib import admin

from .models import Cliente, DireccionCliente, Repartidor


class DireccionInline(admin.TabularInline):
    model = DireccionCliente
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo_documento", "numero_documento", "telefono", "activo")
    list_filter = ("tipo_documento", "activo")
    search_fields = ("nombre", "numero_documento", "telefono", "email")
    inlines = [DireccionInline]


@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "zona", "vehiculo", "placa", "disponible", "activo")
    list_filter = ("disponible", "activo")
