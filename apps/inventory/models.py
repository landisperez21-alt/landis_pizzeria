from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import F


class Insumo(models.Model):
    class Unidad(models.TextChoices):
        KILO = "kg", "Kilogramo"
        GRAMO = "g", "Gramo"
        LITRO = "lt", "Litro"
        MILILITRO = "ml", "Mililitro"
        UNIDAD = "und", "Unidad"
        PORCION = "porc", "Porcion"

    codigo = models.CharField("Codigo", max_length=20, unique=True)
    nombre = models.CharField("Insumo", max_length=100)
    unidad = models.CharField("Unidad", max_length=6, choices=Unidad.choices, default=Unidad.UNIDAD)
    stock = models.DecimalField("Stock actual", max_digits=12, decimal_places=3, default=Decimal("0.000"))
    stock_minimo = models.DecimalField("Stock minimo", max_digits=12, decimal_places=3, default=Decimal("0.000"))
    costo_unitario = models.DecimalField("Costo unitario", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    activo = models.BooleanField("Activo", default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo

    @property
    def valor_stock(self):
        return (self.stock * self.costo_unitario).quantize(Decimal("0.01"))


class MovimientoInsumo(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada (compra)"
        SALIDA = "salida", "Salida (consumo)"
        AJUSTE = "ajuste", "Ajuste de inventario"

    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField("Tipo", max_length=10, choices=Tipo.choices)
    cantidad = models.DecimalField("Cantidad", max_digits=12, decimal_places=3)
    motivo = models.CharField("Motivo", max_length=200, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de insumo"
        verbose_name_plural = "Movimientos de insumos"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} {self.insumo.unidad} - {self.insumo.nombre}"

    def aplicar(self):
        """Ajusta el stock del insumo segun el tipo de movimiento."""
        if self.tipo == self.Tipo.ENTRADA:
            Insumo.objects.filter(pk=self.insumo_id).update(stock=F("stock") + self.cantidad)
        elif self.tipo == self.Tipo.SALIDA:
            Insumo.objects.filter(pk=self.insumo_id).update(stock=F("stock") - self.cantidad)
        else:
            Insumo.objects.filter(pk=self.insumo_id).update(stock=self.cantidad)
        self.insumo.refresh_from_db(fields=["stock"])
