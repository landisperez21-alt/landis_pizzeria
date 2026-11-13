from django.conf import settings
from django.db import models


class Cliente(models.Model):
    class Documento(models.TextChoices):
        DNI = "DNI", "DNI"
        RUC = "RUC", "RUC"
        CE = "CE", "Carnet de extranjeria"
        SIN = "SIN", "Sin documento"

    nombre = models.CharField("Nombre o razon social", max_length=150)
    tipo_documento = models.CharField("Documento", max_length=10, choices=Documento.choices, default=Documento.DNI)
    numero_documento = models.CharField("Numero de documento", max_length=20, blank=True)
    telefono = models.CharField("Telefono", max_length=20, blank=True)
    email = models.EmailField("Correo", blank=True)
    direccion = models.CharField("Direccion principal", max_length=200, blank=True)
    referencia = models.CharField("Referencia", max_length=200, blank=True)
    notas = models.TextField("Notas", blank=True)
    activo = models.BooleanField("Activo", default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def pedidos_count(self):
        return self.pedidos.count()


class DireccionCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="direcciones")
    direccion = models.CharField("Direccion", max_length=200)
    referencia = models.CharField("Referencia", max_length=200, blank=True)
    distrito = models.CharField("Distrito / zona", max_length=80, blank=True)
    principal = models.BooleanField("Principal", default=False)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Direccion de cliente"
        verbose_name_plural = "Direcciones de clientes"
        ordering = ["-principal", "direccion"]

    def __str__(self):
        return f"{self.direccion} ({self.cliente})"


class Repartidor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="repartidor",
        verbose_name="Usuario",
    )
    zona = models.CharField("Zona de reparto", max_length=80, blank=True)
    vehiculo = models.CharField("Vehiculo", max_length=60, blank=True, help_text="Moto, auto, bicicleta...")
    placa = models.CharField("Placa", max_length=15, blank=True)
    disponible = models.BooleanField("Disponible", default=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Repartidor"
        verbose_name_plural = "Repartidores"
        ordering = ["usuario__first_name"]

    def __str__(self):
        return f"{self.usuario} - {self.zona or 'sin zona'}"
