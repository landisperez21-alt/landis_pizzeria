from django.urls import path

from apps.core.crud import CrudConfig

from .forms import ClienteForm, DireccionClienteForm, RepartidorForm
from .models import Cliente, DireccionCliente, Repartidor

app_name = "customers"

clientes = CrudConfig(
    Cliente, ClienteForm, "Clientes", "customers:clientes", singular="Cliente",
    columnas=[
        {"label": "Cliente", "campo": "nombre"},
        {"label": "Documento", "campo": "numero_documento"},
        {"label": "Telefono", "campo": "telefono"},
        {"label": "Direccion", "campo": "direccion"},
        {"label": "Pedidos", "campo": "pedidos_count", "tipo": "numero"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("nombre", "numero_documento", "telefono", "email"),
    roles=("admin", "cajero"),
)

direcciones = CrudConfig(
    DireccionCliente, DireccionClienteForm, "Direcciones de clientes", "customers:direcciones", singular="Direccion",
    columnas=[
        {"label": "Cliente", "campo": "cliente.nombre"},
        {"label": "Direccion", "campo": "direccion"},
        {"label": "Distrito", "campo": "distrito"},
        {"label": "Principal", "campo": "principal", "tipo": "bool", "texto_true": "Si", "texto_false": "No"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("direccion", "distrito", "cliente__nombre"),
    roles=("admin", "cajero"),
)

repartidores = CrudConfig(
    Repartidor, RepartidorForm, "Repartidores", "customers:repartidores", singular="Repartidor",
    columnas=[
        {"label": "Repartidor", "campo": "usuario.nombre_corto"},
        {"label": "Zona", "campo": "zona"},
        {"label": "Vehiculo", "campo": "vehiculo"},
        {"label": "Placa", "campo": "placa"},
        {"label": "Disponible", "campo": "disponible", "tipo": "bool", "texto_true": "Si", "texto_false": "No"},
        {"label": "Estado", "campo": "activo", "tipo": "bool"},
    ],
    campos_busqueda=("usuario__first_name", "usuario__last_name", "zona", "placa"),
    roles=("admin",),
)

urlpatterns = [
    path("", clientes.lista, name="clientes"),
    path("nuevo/", clientes.crear, name="clientes-crear"),
    path("<int:pk>/editar/", clientes.editar, name="clientes-editar"),
    path("<int:pk>/alternar/", clientes.alternar, name="clientes-alternar"),

    path("direcciones/", direcciones.lista, name="direcciones"),
    path("direcciones/nueva/", direcciones.crear, name="direcciones-crear"),
    path("direcciones/<int:pk>/editar/", direcciones.editar, name="direcciones-editar"),
    path("direcciones/<int:pk>/alternar/", direcciones.alternar, name="direcciones-alternar"),

    path("repartidores/", repartidores.lista, name="repartidores"),
    path("repartidores/nuevo/", repartidores.crear, name="repartidores-crear"),
    path("repartidores/<int:pk>/editar/", repartidores.editar, name="repartidores-editar"),
    path("repartidores/<int:pk>/alternar/", repartidores.alternar, name="repartidores-alternar"),
]
