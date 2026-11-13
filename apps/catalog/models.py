from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    """Agrupacion de la carta: pizzas, combos, bebidas, entradas, postres."""

    nombre = models.CharField("Nombre", max_length=80, unique=True)
    descripcion = models.CharField("Descripcion", max_length=200, blank=True)
    orden = models.PositiveIntegerField("Orden", default=0)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Tamano(models.Model):
    """Tamano de pizza (personal, mediana, familiar)."""

    nombre = models.CharField("Nombre", max_length=40, unique=True)
    porciones = models.PositiveIntegerField("Porciones", default=1)
    factor_precio = models.DecimalField(
        "Factor de precio", max_digits=4, decimal_places=2, default=Decimal("1.00"),
        help_text="Multiplicador sobre el precio base del producto.",
    )
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Tamano"
        verbose_name_plural = "Tamanos"
        ordering = ["factor_precio"]

    def __str__(self):
        return f"{self.nombre} ({self.porciones} porciones)"


class Ingrediente(models.Model):
    """Ingrediente extra que se puede agregar a una pizza."""

    nombre = models.CharField("Nombre", max_length=80, unique=True)
    precio_extra = models.DecimalField("Precio extra", max_digits=8, decimal_places=2, default=Decimal("0.00"))
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Ingrediente extra"
        verbose_name_plural = "Ingredientes extra"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class Tipo(models.TextChoices):
        PIZZA = "pizza", "Pizza"
        COMBO = "combo", "Combo"
        BEBIDA = "bebida", "Bebida"
        ENTRADA = "entrada", "Entrada"
        POSTRE = "postre", "Postre"

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos", verbose_name="Categoria")
    nombre = models.CharField("Nombre", max_length=120)
    tipo = models.CharField("Tipo", max_length=20, choices=Tipo.choices, default=Tipo.PIZZA)
    descripcion = models.TextField("Descripcion", blank=True)
    precio_base = models.DecimalField(
        "Precio base", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Para pizzas es el precio de la porcion mediana (se ajusta por tamano).",
    )
    imagen = models.ImageField("Imagen", upload_to="productos/", blank=True, null=True)
    destacado = models.BooleanField("Destacado", default=False)
    activo = models.BooleanField("Activo", default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["categoria__orden", "nombre"]

    def __str__(self):
        return self.nombre

    @property
    def es_pizza(self):
        return self.tipo == self.Tipo.PIZZA

    def precio_para(self, tamano=None):
        """Devuelve el precio del producto segun el tamano elegido."""
        if self.es_pizza and tamano is not None:
            return (self.precio_base * tamano.factor_precio).quantize(Decimal("0.10"))
        return self.precio_base


class RecetaItem(models.Model):
    """Cantidad de un insumo que consume un producto al prepararse."""

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="receta")
    insumo = models.ForeignKey("inventory.Insumo", on_delete=models.PROTECT, related_name="recetas", verbose_name="Insumo")
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=3, default=Decimal("0.000"))

    class Meta:
        verbose_name = "Ingrediente de receta"
        verbose_name_plural = "Receta (insumos)"
        unique_together = ("producto", "insumo")

    def __str__(self):
        return f"{self.cantidad} de {self.insumo} para {self.producto}"


class ComboItem(models.Model):
    """Producto incluido dentro de un combo."""

    combo = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="items_combo")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="en_combos")
    cantidad = models.PositiveIntegerField("Cantidad", default=1)

    class Meta:
        verbose_name = "Item de combo"
        verbose_name_plural = "Items de combo"
        unique_together = ("combo", "producto")

    def __str__(self):
        return f"{self.cantidad} x {self.producto} en {self.combo}"
