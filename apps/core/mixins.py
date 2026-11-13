from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class RolRequiredMixin(LoginRequiredMixin):
    """Restringe una vista a los roles indicados en `roles_permitidos`."""

    roles_permitidos = ()
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.roles_permitidos and request.user.rol not in self.roles_permitidos:
            messages.error(request, "No tienes permisos para acceder a esta seccion.")
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RolRequiredMixin):
    roles_permitidos = ("admin",)


class GestionRequiredMixin(RolRequiredMixin):
    """Administrador y cajero: personal de gestion."""

    roles_permitidos = ("admin", "cajero")
