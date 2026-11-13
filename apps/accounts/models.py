from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario del sistema con un rol operativo."""

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        CAJERO = "cajero", "Cajero"
        COCINERO = "cocinero", "Cocinero"
        REPARTIDOR = "repartidor", "Repartidor"

    rol = models.CharField("Rol", max_length=20, choices=Rol.choices, default=Rol.CAJERO)
    telefono = models.CharField("Telefono", max_length=20, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["first_name", "username"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def nombre_corto(self):
        return self.get_full_name() or self.username

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def es_cajero(self):
        return self.rol == self.Rol.CAJERO

    @property
    def es_cocinero(self):
        return self.rol == self.Rol.COCINERO

    @property
    def es_repartidor(self):
        return self.rol == self.Rol.REPARTIDOR
