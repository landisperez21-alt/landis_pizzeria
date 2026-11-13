from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.db.models import Sum


class Pedido(models.Model):
    class Tipo(models.TextChoices):
        MESA = "mesa", "En mesa"
        LLEVAR = "llevar", "Para llevar"
        DELIVERY = "delivery", "Delivery"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PREPARACION = "en_preparacion", "En preparacion"
        HORNEANDO = "horneando", "Horneando"
        LISTO = "listo", "Listo"
        EN_CAMINO = "en_camino", "En camino"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    codigo = models.CharField("Codigo", max_length=15, unique=True, blank=True)
    cliente = models.ForeignKey(
        "customers.Cliente", on_delete=models.PROTECT, related_name="pedidos", verbose_name="Cliente"
    )
    tipo = models.CharField("Tipo", max_length=10, choices=Tipo.choices, default=Tipo.DELIVERY)
    estado = models.CharField("Estado", max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    mesa = models.CharField("Mesa", max_length=10, blank=True)
    direccion = models.CharField("Direccion de entrega", max_length=200, blank=True)
    repartidor = models.ForeignKey(
        "customers.Repartidor", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pedidos", verbose_name="Repartidor",
    )
    notas = models.TextField("Notas", blank=True)
    costo_delivery = models.DecimalField("Costo de delivery", max_digits=8, decimal_places=2, default=Decimal("0.00"))
    descuento = models.DecimalField("Descuento", max_digits=8, decimal_places=2, default=Decimal("0.00"))
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pedidos", verbose_name="Registrado por",
    )
    creado_en = models.DateTimeField("Creado", auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    entregado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado_en"]

    def __str__(self):
        return self.codigo or f"Pedido {self.pk}"

    def save(self, *args, **kwargs):
        nuevo = self.pk is None
        super().save(*args, **kwargs)
        if not self.codigo:
            self.codigo = f"PED-{self.pk:05d}"
            super().save(update_fields=["codigo"])

    @property
    def subtotal(self):
        total = self.detalles.aggregate(t=Sum("subtotal_cache"))["t"] or Decimal("0.00")
        return total

    @property
    def total(self):
        return (self.subtotal + self.costo_delivery - self.descuento).quantize(Decimal("0.10"))

    @property
    def total_pagado(self):
        return self.pagos.filter(estado="registrado").aggregate(t=Sum("monto"))["t"] or Decimal("0.00")

    @property
    def saldo(self):
        return (self.total - self.total_pagado).quantize(Decimal("0.10"))

    @property
    def esta_pagado(self):
        return self.saldo <= 0

    @property
    def color_estado(self):
        return {
            "pendiente": "secondary",
            "en_preparacion": "info",
            "horneando": "warning",
            "listo": "primary",
            "en_camino": "info",
            "entregado": "success",
            "cancelado": "danger",
        }.get(self.estado, "secondary")

    def recalcular(self):
        self.save(update_fields=["actualizado_en"])

    @transaction.atomic
    def descontar_insumos(self):
        """Descuenta del inventario los insumos de la receta de cada producto."""
        from apps.inventory.models import MovimientoInsumo

        for detalle in self.detalles.select_related("producto"):
            for item in detalle.producto.receta.select_related("insumo"):
                cantidad = item.cantidad * detalle.cantidad
                if cantidad <= 0:
                    continue
                mov = MovimientoInsumo.objects.create(
                    insumo=item.insumo, tipo=MovimientoInsumo.Tipo.SALIDA,
                    cantidad=cantidad, motivo=f"Pedido {self.codigo}", usuario=self.usuario,
                )
                mov.aplicar()


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey("catalog.Producto", on_delete=models.PROTECT, related_name="detalles")
    tamano = models.ForeignKey("catalog.Tamano", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tamano")
    cantidad = models.PositiveIntegerField("Cantidad", default=1)
    precio_unitario = models.DecimalField("Precio unitario", max_digits=8, decimal_places=2, default=Decimal("0.00"))
    notas = models.CharField("Notas", max_length=200, blank=True)
    subtotal_cache = models.DecimalField("Subtotal", max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"

    def calcular(self):
        if self.pk is None:
            extras = Decimal("0.00")
        else:
            extras = self.extras.aggregate(t=Sum("precio"))["t"] or Decimal("0.00")
        self.subtotal_cache = ((self.precio_unitario + extras) * self.cantidad).quantize(Decimal("0.10"))
        return self.subtotal_cache

    def save(self, *args, **kwargs):
        self.calcular()
        super().save(*args, **kwargs)


class DetalleExtra(models.Model):
    detalle = models.ForeignKey(DetallePedido, on_delete=models.CASCADE, related_name="extras")
    ingrediente = models.ForeignKey("catalog.Ingrediente", on_delete=models.PROTECT, verbose_name="Ingrediente")
    precio = models.DecimalField("Precio", max_digits=8, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "Ingrediente extra del detalle"
        verbose_name_plural = "Ingredientes extra del detalle"

    def __str__(self):
        return str(self.ingrediente)

    def save(self, *args, **kwargs):
        if not self.precio:
            self.precio = self.ingrediente.precio_extra
        super().save(*args, **kwargs)
