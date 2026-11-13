from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.orders.models import Pedido

from .forms import CierreCajaForm, PagoForm, SesionCajaForm
from .models import Pago, SesionCaja


def sesion_abierta(usuario):
    return SesionCaja.objects.filter(usuario=usuario, fecha_cierre__isnull=True).first()


@login_required
def lista(request):
    qs = Pago.objects.select_related("pedido", "metodo", "usuario")
    estado = request.GET.get("estado", "")
    q = request.GET.get("q", "").strip()
    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(Q(pedido__codigo__icontains=q) | Q(referencia_operacion__icontains=q))
    total = qs.filter(estado="registrado").aggregate(t=Sum("monto"))["t"] or Decimal("0.00")
    return render(request, "payments/lista.html", {
        "titulo": "Pagos",
        "pagos": qs[:200],
        "estado": estado,
        "q": q,
        "total": total,
    })


@login_required
def crear(request):
    inicial = {}
    pedido_id = request.GET.get("pedido")
    if pedido_id:
        pedido = Pedido.objects.filter(pk=pedido_id).first()
        if pedido:
            inicial = {"pedido": pedido, "monto": pedido.saldo if pedido.saldo > 0 else pedido.total}
    form = PagoForm(request.POST or None, initial=inicial)
    if request.method == "POST" and form.is_valid():
        pago = form.save(commit=False)
        pedido = pago.pedido
        if pago.monto > pedido.saldo + Decimal("0.001"):
            messages.error(request, f"El monto supera el saldo pendiente ({pedido.saldo}).")
        else:
            pago.usuario = request.user
            pago.sesion_caja = sesion_abierta(request.user)
            pago.save()
            messages.success(request, f"Pago registrado para {pedido.codigo}.")
            return redirect("orders:detalle", pk=pedido.pk)
    return render(request, "payments/form.html", {"titulo": "Registrar pago", "form": form})


@login_required
def anular(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    if request.method == "POST":
        pago.estado = Pago.Estado.ANULADO
        pago.save(update_fields=["estado"])
        messages.success(request, "Pago anulado.")
        return redirect("orders:detalle", pk=pago.pedido_id)
    return redirect("payments:lista")


@login_required
def caja(request):
    actual = sesion_abierta(request.user)
    sesiones = SesionCaja.objects.select_related("usuario")[:30]
    return render(request, "payments/caja.html", {
        "titulo": "Caja",
        "actual": actual,
        "sesiones": sesiones,
        "form_apertura": SesionCajaForm(),
        "form_cierre": CierreCajaForm(instance=actual) if actual else None,
    })


@login_required
def abrir_caja(request):
    if request.method == "POST":
        if sesion_abierta(request.user):
            messages.error(request, "Ya tienes una caja abierta.")
        else:
            form = SesionCajaForm(request.POST)
            if form.is_valid():
                sesion = form.save(commit=False)
                sesion.usuario = request.user
                sesion.save()
                messages.success(request, "Caja abierta.")
    return redirect("payments:caja")


@login_required
def cerrar_caja(request, pk):
    sesion = get_object_or_404(SesionCaja, pk=pk)
    if request.method == "POST" and sesion.abierta:
        form = CierreCajaForm(request.POST, instance=sesion)
        if form.is_valid():
            sesion = form.save(commit=False)
            sesion.fecha_cierre = timezone.now()
            sesion.save()
            messages.success(request, "Caja cerrada.")
    return redirect("payments:caja")
