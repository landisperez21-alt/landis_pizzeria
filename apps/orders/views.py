from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.catalog.models import Ingrediente, Producto, Tamano

from .forms import DetallePedidoForm, PedidoForm
from .models import DetalleExtra, DetallePedido, Pedido

ESTADOS_FLUJO = ["pendiente", "en_preparacion", "horneando", "listo", "en_camino", "entregado"]


@login_required
def lista(request):
    qs = Pedido.objects.select_related("cliente", "repartidor")
    estado = request.GET.get("estado", "")
    tipo = request.GET.get("tipo", "")
    q = request.GET.get("q", "").strip()
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if q:
        qs = qs.filter(Q(codigo__icontains=q) | Q(cliente__nombre__icontains=q))
    return render(request, "orders/lista.html", {
        "titulo": "Pedidos",
        "pedidos": qs[:200],
        "estado": estado,
        "tipo": tipo,
        "q": q,
        "estados": Pedido.Estado.choices,
        "tipos": Pedido.Tipo.choices,
    })


@login_required
def detalle(request, pk):
    pedido = get_object_or_404(Pedido.objects.select_related("cliente", "repartidor"), pk=pk)
    return render(request, "orders/detalle.html", {
        "titulo": f"Pedido {pedido.codigo}",
        "pedido": pedido,
        "detalles": pedido.detalles.select_related("producto", "tamano").prefetch_related("extras"),
        "form_item": DetallePedidoForm(),
        "productos": Producto.objects.filter(activo=True).select_related("categoria"),
        "tamanos": Tamano.objects.filter(activo=True),
        "ingredientes": Ingrediente.objects.filter(activo=True),
        "estados": Pedido.Estado.choices,
        "productos_json": [
            {"pk": p.pk, "nombre": p.nombre, "base": str(p.precio_base), "pizza": p.es_pizza}
            for p in Producto.objects.filter(activo=True)
        ],
        "tamanos_json": [
            {"pk": t.pk, "factor": str(t.factor_precio)} for t in Tamano.objects.filter(activo=True)
        ],
    })


@login_required
def crear(request):
    form = PedidoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pedido = form.save(commit=False)
        pedido.usuario = request.user
        pedido.save()
        messages.success(request, f"Pedido {pedido.codigo} creado. Agrega los productos.")
        return redirect("orders:detalle", pk=pedido.pk)
    return render(request, "orders/form.html", {"titulo": "Nuevo pedido", "form": form})


@login_required
def editar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pedido actualizado.")
        return redirect("orders:detalle", pk=pedido.pk)
    return render(request, "orders/form.html", {"titulo": f"Editar {pedido.codigo}", "form": form, "pedido": pedido})


@login_required
def agregar_item(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method != "POST":
        return redirect("orders:detalle", pk=pk)
    form = DetallePedidoForm(request.POST)
    if form.is_valid():
        detalle = form.save(commit=False)
        detalle.pedido = pedido
        detalle.precio_unitario = detalle.producto.precio_para(detalle.tamano)
        detalle.save()
        for ingrediente_id in request.POST.getlist("extras"):
            ingrediente = Ingrediente.objects.filter(pk=ingrediente_id, activo=True).first()
            if ingrediente:
                DetalleExtra.objects.create(detalle=detalle, ingrediente=ingrediente, precio=ingrediente.precio_extra)
        detalle.calcular()
        detalle.save(update_fields=["subtotal_cache"])
        messages.success(request, "Producto agregado al pedido.")
    else:
        messages.error(request, "No se pudo agregar el producto. Revisa los datos.")
    return redirect("orders:detalle", pk=pk)


@login_required
def eliminar_item(request, pk, item_pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == "POST":
        DetallePedido.objects.filter(pk=item_pk, pedido=pedido).delete()
        messages.success(request, "Producto eliminado del pedido.")
    return redirect("orders:detalle", pk=pk)


@login_required
def cambiar_estado(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == "POST":
        nuevo = request.POST.get("estado")
        if nuevo in dict(Pedido.Estado.choices):
            anterior = pedido.estado
            pedido.estado = nuevo
            if nuevo == Pedido.Estado.ENTREGADO and anterior != Pedido.Estado.ENTREGADO:
                pedido.entregado_en = timezone.now()
                if not pedido.detalles.exists():
                    messages.warning(request, "El pedido no tiene productos.")
                else:
                    pedido.descontar_insumos()
            pedido.save()
            messages.success(request, f"Estado actualizado a {pedido.get_estado_display()}.")
    return redirect("orders:detalle", pk=pk)


@login_required
def comanda(request, pk):
    pedido = get_object_or_404(Pedido.objects.select_related("cliente"), pk=pk)
    return render(request, "orders/comanda.html", {
        "pedido": pedido,
        "detalles": pedido.detalles.select_related("producto", "tamano").prefetch_related("extras"),
    })
