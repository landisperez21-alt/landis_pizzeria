from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import MovimientoInsumoForm
from .models import MovimientoInsumo


@login_required
def movimientos(request):
    registros = MovimientoInsumo.objects.select_related("insumo", "usuario")[:100]
    form = MovimientoInsumoForm()
    return render(request, "inventory/movimientos.html", {
        "titulo": "Movimientos de insumos",
        "movimientos": registros,
        "form": form,
    })


@login_required
def registrar_movimiento(request):
    if request.method != "POST":
        return redirect("inventory:movimientos")
    form = MovimientoInsumoForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            movimiento.aplicar()
        messages.success(request, f"Movimiento registrado: {movimiento}.")
    else:
        messages.error(request, "No se pudo registrar el movimiento. Revisa los datos.")
    return redirect("inventory:movimientos")
