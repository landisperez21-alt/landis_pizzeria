from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from apps.catalog.models import Producto
from apps.customers.models import Cliente
from apps.inventory.models import Insumo
from apps.orders.models import DetallePedido, Pedido
from apps.payments.models import Pago


ESTADOS_ACTIVOS = ["pendiente", "en_preparacion", "horneando", "listo", "en_camino"]


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=6)

    pedidos_hoy = Pedido.objects.filter(creado_en__date=hoy)
    ventas_hoy = (
        Pago.objects.filter(estado="registrado", fecha_pago__date=hoy)
        .aggregate(total=Sum("monto"))["total"]
        or Decimal("0.00")
    )
    ticket_promedio = Decimal("0.00")
    if pedidos_hoy.exists():
        ticket_promedio = ventas_hoy / pedidos_hoy.count()

    # Ventas de los ultimos 7 dias para el grafico
    ventas_por_dia = (
        Pago.objects.filter(estado="registrado", fecha_pago__date__gte=inicio_semana)
        .annotate(dia=TruncDate("fecha_pago"))
        .values("dia")
        .annotate(total=Sum("monto"))
        .order_by("dia")
    )
    mapa_ventas = {v["dia"]: float(v["total"]) for v in ventas_por_dia}
    serie_labels, serie_valores = [], []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        serie_labels.append(dia.strftime("%d/%m"))
        serie_valores.append(mapa_ventas.get(dia, 0.0))

    # Pedidos por estado
    por_estado = (
        Pedido.objects.values("estado").annotate(total=Count("id")).order_by("-total")
    )
    estado_map = dict(Pedido.Estado.choices)
    estados_labels = [estado_map.get(e["estado"], e["estado"]) for e in por_estado]
    estados_valores = [e["total"] for e in por_estado]

    # Productos mas vendidos (top 5)
    top_productos = (
        DetallePedido.objects.filter(pedido__estado__in=ESTADOS_ACTIVOS + ["entregado"])
        .values(nombre=F("producto__nombre"))
        .annotate(cantidad=Sum("cantidad"))
        .order_by("-cantidad")[:5]
    )

    insumos_bajos = Insumo.objects.filter(activo=True, stock__lte=F("stock_minimo")).order_by("stock")[:6]

    contexto = {
        "titulo": "Panel de control",
        "pedidos_hoy": pedidos_hoy.count(),
        "ventas_hoy": ventas_hoy,
        "ticket_promedio": ticket_promedio,
        "pedidos_activos": Pedido.objects.filter(estado__in=ESTADOS_ACTIVOS).count(),
        "clientes_total": Cliente.objects.filter(activo=True).count(),
        "productos_total": Producto.objects.filter(activo=True).count(),
        "insumos_bajos": insumos_bajos,
        "top_productos": top_productos,
        "pedidos_recientes": Pedido.objects.select_related("cliente", "repartidor").order_by("-creado_en")[:8],
        "serie_labels": serie_labels,
        "serie_valores": serie_valores,
        "estados_labels": estados_labels,
        "estados_valores": estados_valores,
    }
    return render(request, "core/dashboard.html", contexto)


@login_required
def reportes(request):
    hoy = timezone.now().date()
    desde = request.GET.get("desde") or (hoy - timedelta(days=29)).isoformat()
    hasta = request.GET.get("hasta") or hoy.isoformat()

    pagos = Pago.objects.filter(
        estado="registrado", fecha_pago__date__gte=desde, fecha_pago__date__lte=hasta
    )
    total_ventas = pagos.aggregate(total=Sum("monto"))["total"] or Decimal("0.00")

    por_metodo = (
        pagos.values("metodo__nombre").annotate(total=Sum("monto"), n=Count("id")).order_by("-total")
    )
    por_tipo_pedido = (
        Pedido.objects.filter(creado_en__date__gte=desde, creado_en__date__lte=hasta)
        .values("tipo")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    tipo_map = dict(Pedido.Tipo.choices)
    top_productos = (
        DetallePedido.objects.filter(
            pedido__creado_en__date__gte=desde, pedido__creado_en__date__lte=hasta
        )
        .values(nombre=F("producto__nombre"))
        .annotate(cantidad=Sum("cantidad"), ingreso=Sum("subtotal_cache"))
        .order_by("-cantidad")[:10]
    )
    por_repartidor = (
        Pedido.objects.filter(
            tipo="delivery",
            repartidor__isnull=False,
            creado_en__date__gte=desde,
            creado_en__date__lte=hasta,
        )
        .values(nombre=F("repartidor__usuario__first_name"))
        .annotate(entregas=Count("id"))
        .order_by("-entregas")
    )

    contexto = {
        "titulo": "Reportes",
        "desde": desde,
        "hasta": hasta,
        "total_ventas": total_ventas,
        "cantidad_pagos": pagos.count(),
        "por_metodo": por_metodo,
        "por_tipo_pedido": [
            {"tipo": tipo_map.get(t["tipo"], t["tipo"]), "total": t["total"]} for t in por_tipo_pedido
        ],
        "top_productos": top_productos,
        "por_repartidor": por_repartidor,
        "pedidos_total": Pedido.objects.filter(
            creado_en__date__gte=desde, creado_en__date__lte=hasta
        ).count(),
    }
    return render(request, "core/reportes.html", contexto)


def error_403(request, exception=None):
    return render(request, "core/403.html", status=403)


def error_404(request, exception=None):
    return render(request, "core/404.html", status=404)


def error_500(request):
    return render(request, "core/500.html", status=500)
