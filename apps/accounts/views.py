from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from apps.core.mixins import AdminRequiredMixin

from .forms import LoginForm, UsuarioForm
from .models import Usuario


class IngresarView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Bienvenido, {form.get_user().nombre_corto}.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contrasena incorrectos.")
        return super().form_invalid(form)


class SalirView(LogoutView):
    next_page = reverse_lazy("accounts:login")


@login_required
def lista(request):
    q = request.GET.get("q", "").strip()
    usuarios = Usuario.objects.all()
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
            | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    return render(request, "accounts/lista.html", {"titulo": "Usuarios del sistema", "usuarios": usuarios, "q": q})


@login_required
def crear(request):
    if not request.user.es_admin:
        messages.error(request, "Solo un administrador puede gestionar usuarios.")
        return redirect("core:dashboard")
    form = UsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario registrado correctamente.")
        return redirect("accounts:lista")
    return render(request, "accounts/form.html", {"titulo": "Nuevo usuario", "form": form})


@login_required
def editar(request, pk):
    if not request.user.es_admin:
        messages.error(request, "Solo un administrador puede gestionar usuarios.")
        return redirect("core:dashboard")
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(request.POST or None, instance=usuario)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario actualizado.")
        return redirect("accounts:lista")
    return render(request, "accounts/form.html", {"titulo": f"Editar {usuario}", "form": form, "objeto": usuario})


@login_required
@require_POST
def alternar_activo(request, pk):
    if not request.user.es_admin:
        messages.error(request, "Solo un administrador puede gestionar usuarios.")
        return redirect("core:dashboard")
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
        return redirect("accounts:lista")
    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    estado = "activado" if usuario.is_active else "desactivado"
    messages.success(request, f"Usuario {estado}.")
    return redirect("accounts:lista")


@login_required
def perfil(request):
    form = UsuarioForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado.")
        return redirect("accounts:perfil")
    return render(request, "accounts/perfil.html", {"titulo": "Mi perfil", "form": form})
