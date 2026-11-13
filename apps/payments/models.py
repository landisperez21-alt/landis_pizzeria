from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class MetodoPago(models.Model):
    nombre = models.CharField("Metodo", max_length=50, unique=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Metodo de pago"
        verbose_name_plural = "Metodos de pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class SesionCaja(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sesiones_caja")
    fecha_apertura = models.DateTimeField("Apertura", auto_now_add=True)
    monto_inicial = models.DecimalField("Monto inicial", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    fecha_cierre = models.DateTimeField("Cierre", null=True, blank=True)
    monto_final = models.DecimalField("Monto final", max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.CharField("Observaciones", max_length=255, blank=True)

    class Meta:
        verbose_name = "Sesion de caja"
        verbose_name_plural = "Sesiones de caja"
        ordering = ["-fecha_apertura"]

    def __str__(self):
        return f"Caja #{self.pk} - {self.usuario}"

    @property
    def abierta(self):
        return self.fecha_cierre is None

    @property
    def total_cobrado(self):
        return self.pagos.filter(estado="registrado").aggregate(t=Sum("monto"))["t"] or Decimal("0.00")


class Pago(models.Model):
    class Estado(models.TextChoices):
        REGISTRADO = "registrado", "Registrado"
        ANULADO = "anulado", "Anulado"

    pedido = models.ForeignKey("orders.Pedido", on_delete=models.PROTECT, related_name="pagos", verbose_name="Pedido")
    metodo = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name="pagos", verbose_name="Metodo de pago")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Cobrado por")
    sesion_caja = models.ForeignKey(SesionCaja, on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos")
    monto = models.DecimalField("Monto", max_digits=10, decimal_places=2)
    referencia_operacion = models.CharField("Nro. de operacion", max_length=100, blank=True)
    estado = models.CharField("Estado", max_length=12, choices=Estado.choices, default=Estado.REGISTRADO)
    observaciones = models.CharField("Observaciones", max_length=255, blank=True)
    fecha_pago = models.DateTimeField("Fecha de pago", auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha_pago"]

    def __str__(self):
        return f"{self.pedido.codigo} - {self.metodo} - {self.monto}"
