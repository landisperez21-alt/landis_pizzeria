"""Carga datos de demostracion para la Pizzeria Don Landinis.

Uso:
    python manage.py datos_demo
    python manage.py datos_demo --limpiar   # borra pedidos/pagos antes de recargar

Es idempotente: usa get_or_create para no duplicar registros.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Usuario
from apps.catalog.models import (
    Categoria, ComboItem, Ingrediente, Producto, RecetaItem, Tamano,
)
from apps.customers.models import Cliente, DireccionCliente, Repartidor
from apps.inventory.models import Insumo, MovimientoInsumo
from apps.orders.models import DetalleExtra, DetallePedido, Pedido
from apps.payments.models import MetodoPago, Pago

D = Decimal


class Command(BaseCommand):
    help = "Carga datos de demostracion (usuarios, carta, inventario, clientes y pedidos)."

    def add_arguments(self, parser):
        parser.add_argument("--limpiar", action="store_true", help="Elimina pedidos y pagos antes de recargar.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["limpiar"]:
            Pago.objects.all().delete()
            DetalleExtra.objects.all().delete()
            DetallePedido.objects.all().delete()
            Pedido.objects.all().delete()
            MovimientoInsumo.objects.all().delete()
            self.stdout.write(self.style.WARNING("Pedidos, pagos y movimientos eliminados."))

        self.usuarios()
        tamanos = self.tamanos()
        ingredientes = self.ingredientes()
        insumos = self.insumos()
        productos = self.productos(insumos)
        self.combos(productos)
        clientes = self.clientes()
        repartidores = self.repartidores()
        metodos = self.metodos_pago()
        self.pedidos(clientes, repartidores, metodos, tamanos, ingredientes)

        self.stdout.write(self.style.SUCCESS("\nDatos de demostracion cargados correctamente."))
        self.stdout.write("  Admin:    admin / DonLandinis2026")
        self.stdout.write("  Cajero:   cajero / Cajero2026")
        self.stdout.write("  Cocinero: cocinero / Cocina2026")
        self.stdout.write("  Reparto:  repartidor / Reparto2026")

    # ------------------------------------------------------------------ users
    def usuarios(self):
        datos = [
            ("admin", "Fred", "Perez", "admin", True, True),
            ("cajero", "Lucia", "Ramos", "cajero", False, False),
            ("cocinero", "Marco", "Diaz", "cocinero", False, False),
            ("repartidor", "Julio", "Vargas", "repartidor", False, False),
        ]
        for username, nombre, apellido, rol, is_staff, is_super in datos:
            usuario, creado = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": nombre, "last_name": apellido, "rol": rol,
                    "is_staff": is_staff, "is_superuser": is_super,
                    "email": f"{username}@donlandinis.pe",
                },
            )
            if creado:
                usuario.set_password({
                    "admin": "DonLandinis2026", "cajero": "Cajero2026",
                    "cocinero": "Cocina2026", "repartidor": "Reparto2026",
                }[username])
                usuario.save()
        self.stdout.write("Usuarios listos.")

    # ------------------------------------------------------------------ carta
    def tamanos(self):
        datos = [
            ("Personal", 4, D("0.70")),
            ("Mediana", 8, D("1.00")),
            ("Familiar", 12, D("1.35")),
        ]
        mapa = {}
        for nombre, porciones, factor in datos:
            obj, _ = Tamano.objects.get_or_create(
                nombre=nombre, defaults={"porciones": porciones, "factor_precio": factor}
            )
            mapa[nombre] = obj
        self.stdout.write("Tamanos listos.")
        return mapa

    def ingredientes(self):
        datos = [
            ("Queso extra", "4.00"), ("Pepperoni extra", "5.00"), ("Jamon extra", "5.00"),
            ("Champinones", "4.50"), ("Aceitunas", "3.00"), ("Jalapenos", "3.00"),
            ("Tocino", "6.00"), ("Pina", "3.50"),
        ]
        mapa = {}
        for nombre, precio in datos:
            obj, _ = Ingrediente.objects.get_or_create(
                nombre=nombre, defaults={"precio_extra": D(precio)}
            )
            mapa[nombre] = obj
        self.stdout.write("Ingredientes extra listos.")
        return mapa

    def insumos(self):
        datos = [
            ("INS-001", "Harina", "kg", "40", "10", "4.50"),
            ("INS-002", "Mozzarella", "kg", "18", "5", "28.00"),
            ("INS-003", "Salsa de tomate", "lt", "25", "8", "9.50"),
            ("INS-004", "Pepperoni", "kg", "6", "2", "42.00"),
            ("INS-005", "Jamon", "kg", "7", "2", "34.00"),
            ("INS-006", "Champinones", "kg", "4", "1.5", "22.00"),
            ("INS-007", "Aceitunas", "kg", "3", "1", "18.00"),
            ("INS-008", "Pina en rodajas", "kg", "3", "1", "12.00"),
            ("INS-009", "Tocino", "kg", "2", "1", "38.00"),
            ("INS-010", "Gaseosa 1.5L", "und", "48", "12", "6.50"),
            ("INS-011", "Cerveza botella", "und", "36", "12", "8.00"),
            ("INS-012", "Cajas para pizza", "und", "120", "30", "1.20"),
            ("INS-013", "Alitas de pollo", "kg", "10", "3", "16.00"),
            ("INS-014", "Queso crema (postre)", "kg", "4", "1", "20.00"),
        ]
        mapa = {}
        for codigo, nombre, unidad, stock, minimo, costo in datos:
            obj, _ = Insumo.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre, "unidad": unidad, "stock": D(stock),
                    "stock_minimo": D(minimo), "costo_unitario": D(costo),
                },
            )
            mapa[nombre] = obj
        self.stdout.write("Insumos listos.")
        return mapa

    def productos(self, insumos):
        categorias = {}
        for nombre, desc, orden in [
            ("Pizzas", "Pizzas artesanales al horno", 1),
            ("Combos", "Combos familiares y personales", 2),
            ("Entradas", "Para empezar", 3),
            ("Bebidas", "Gaseosas y cervezas", 4),
            ("Postres", "Dulce final", 5),
        ]:
            obj, _ = Categoria.objects.get_or_create(
                nombre=nombre, defaults={"descripcion": desc, "orden": orden}
            )
            categorias[nombre] = obj

        pizzas = [
            ("Pizza Margarita", "18.00", True, ["Mozzarella", "Salsa de tomate"]),
            ("Pizza Pepperoni", "24.00", True, ["Mozzarella", "Salsa de tomate", "Pepperoni"]),
            ("Pizza Hawaiana", "24.00", False, ["Mozzarella", "Salsa de tomate", "Jamon", "Pina en rodajas"]),
            ("Pizza Americana", "26.00", True, ["Mozzarella", "Salsa de tomate", "Pepperoni", "Tocino"]),
            ("Pizza Vegetariana", "22.00", False, ["Mozzarella", "Salsa de tomate", "Champinones", "Aceitunas"]),
        ]
        productos = {}
        for nombre, precio, destacado, receta in pizzas:
            prod, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "categoria": categorias["Pizzas"], "tipo": Producto.Tipo.PIZZA,
                    "precio_base": D(precio), "destacado": destacado,
                    "descripcion": "Deliciosa pizza preparada al horno.",
                },
            )
            productos[nombre] = prod
            for insumo_nombre in receta:
                RecetaItem.objects.get_or_create(
                    producto=prod, insumo=insumos[insumo_nombre],
                    defaults={"cantidad": D("0.150")},
                )
            RecetaItem.objects.get_or_create(
                producto=prod, insumo=insumos["Harina"], defaults={"cantidad": D("0.250")}
            )

        # Entradas
        alitas, _ = Producto.objects.get_or_create(
            nombre="Alitas BBQ (8 und)",
            defaults={
                "categoria": categorias["Entradas"], "tipo": Producto.Tipo.ENTRADA,
                "precio_base": D("22.00"), "descripcion": "Alitas de pollo con salsa BBQ.",
            },
        )
        productos["Alitas BBQ (8 und)"] = alitas
        RecetaItem.objects.get_or_create(producto=alitas, insumo=insumos["Alitas de pollo"], defaults={"cantidad": D("0.400")})

        # Bebidas
        gaseosa, _ = Producto.objects.get_or_create(
            nombre="Gaseosa 1.5L",
            defaults={"categoria": categorias["Bebidas"], "tipo": Producto.Tipo.BEBIDA, "precio_base": D("10.00")},
        )
        cerveza, _ = Producto.objects.get_or_create(
            nombre="Cerveza artesanal",
            defaults={"categoria": categorias["Bebidas"], "tipo": Producto.Tipo.BEBIDA, "precio_base": D("14.00")},
        )
        productos["Gaseosa 1.5L"] = gaseosa
        productos["Cerveza artesanal"] = cerveza
        RecetaItem.objects.get_or_create(producto=gaseosa, insumo=insumos["Gaseosa 1.5L"], defaults={"cantidad": D("1")})
        RecetaItem.objects.get_or_create(producto=cerveza, insumo=insumos["Cerveza botella"], defaults={"cantidad": D("1")})

        # Postres
        cheesecake, _ = Producto.objects.get_or_create(
            nombre="Cheesecake de fresa",
            defaults={"categoria": categorias["Postres"], "tipo": Producto.Tipo.POSTRE, "precio_base": D("12.00")},
        )
        productos["Cheesecake de fresa"] = cheesecake
        RecetaItem.objects.get_or_create(producto=cheesecake, insumo=insumos["Queso crema (postre)"], defaults={"cantidad": D("0.120")})

        self.stdout.write("Productos y recetas listos.")
        return productos

    def combos(self, productos):
        combo, _ = Producto.objects.get_or_create(
            nombre="Combo Familiar (2 pizzas + gaseosa)",
            defaults={
                "categoria": Categoria.objects.get(nombre="Combos"),
                "tipo": Producto.Tipo.COMBO, "precio_base": D("69.00"), "destacado": True,
                "descripcion": "2 pizzas familiares a eleccion + gaseosa 1.5L.",
            },
        )
        ComboItem.objects.get_or_create(combo=combo, producto=productos["Pizza Pepperoni"], defaults={"cantidad": 2})
        ComboItem.objects.get_or_create(combo=combo, producto=productos["Gaseosa 1.5L"], defaults={"cantidad": 1})

        combo2, _ = Producto.objects.get_or_create(
            nombre="Combo Personal (pizza + gaseosa)",
            defaults={
                "categoria": Categoria.objects.get(nombre="Combos"),
                "tipo": Producto.Tipo.COMBO, "precio_base": D("25.00"),
                "descripcion": "1 pizza personal + gaseosa personal.",
            },
        )
        ComboItem.objects.get_or_create(combo=combo2, producto=productos["Pizza Margarita"], defaults={"cantidad": 1})
        ComboItem.objects.get_or_create(combo=combo2, producto=productos["Gaseosa 1.5L"], defaults={"cantidad": 1})
        self.stdout.write("Combos listos.")

    # --------------------------------------------------------------- clientes
    def clientes(self):
        datos = [
            ("Carlos Quispe Huaman", "DNI", "45123678", "987654321", "Av. Universitaria 456", "Ref. frente al parque"),
            ("Maria Lopez Torres", "DNI", "72345612", "912345678", "Jr. Los Andes 120", "Porton azul"),
            ("Restaurante El Buen Sabor", "RUC", "20556677889", "062123456", "Av. Huanuco 890", "Segundo piso"),
            ("Ana Ramirez Suarez", "DNI", "40889911", "955112233", "Calle Las Flores 33", "Casa de dos pisos"),
            ("Jorge Medina Rojas", "DNI", "70123456", "944556677", "Pasaje El Sol 15", "Cerca a la loza deportiva"),
            ("Rosa Fernandez Cruz", "DNI", "43667788", "933221100", "Av. Centenario 2020", "Frente a la comisaria"),
        ]
        clientes = []
        for nombre, tipo, numero, telefono, direccion, referencia in datos:
            cliente, creado = Cliente.objects.get_or_create(
                numero_documento=numero,
                defaults={
                    "nombre": nombre, "tipo_documento": tipo, "telefono": telefono,
                    "direccion": direccion, "referencia": referencia,
                },
            )
            if creado:
                DireccionCliente.objects.create(
                    cliente=cliente, direccion=direccion, referencia=referencia,
                    distrito="Huanuco", principal=True,
                )
            clientes.append(cliente)
        self.stdout.write("Clientes listos.")
        return clientes

    def repartidores(self):
        repartidores = []
        datos = [
            ("repartidor", "Zona centro", "Moto", "X1-2345"),
        ]
        for username, zona, vehiculo, placa in datos:
            usuario = Usuario.objects.get(username=username)
            obj, _ = Repartidor.objects.get_or_create(
                usuario=usuario,
                defaults={"zona": zona, "vehiculo": vehiculo, "placa": placa},
            )
            repartidores.append(obj)
        self.stdout.write("Repartidores listos.")
        return repartidores

    def metodos_pago(self):
        nombres = ["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia"]
        metodos = []
        for nombre in nombres:
            obj, _ = MetodoPago.objects.get_or_create(nombre=nombre)
            metodos.append(obj)
        self.stdout.write("Metodos de pago listos.")
        return metodos

    # ---------------------------------------------------------------- pedidos
    def pedidos(self, clientes, repartidores, metodos, tamanos, ingredientes):
        if Pedido.objects.exists():
            self.stdout.write("Ya existen pedidos; se omite la generacion de pedidos de ejemplo.")
            return

        random.seed(2026)
        productos_pizza = list(Producto.objects.filter(tipo=Producto.Tipo.PIZZA, activo=True))
        productos_otros = list(Producto.objects.filter(tipo__in=[
            Producto.Tipo.BEBIDA, Producto.Tipo.ENTRADA, Producto.Tipo.POSTRE,
        ], activo=True))
        tamano_lista = list(tamanos.values())
        extra_lista = list(ingredientes.values())
        estados = ["entregado", "entregado", "entregado", "en_camino", "listo",
                   "horneando", "en_preparacion", "pendiente", "cancelado"]
        admin = Usuario.objects.get(username="admin")

        creados = 0
        for i in range(28):
            hace = random.randint(0, 12)
            tipo = random.choice(["delivery", "delivery", "llevar", "mesa"])
            cliente = random.choice(clientes)
            pedido = Pedido(
                cliente=cliente,
                tipo=tipo,
                usuario=admin,
                notas="" if random.random() > 0.3 else "Sin cebolla por favor",
            )
            if tipo == "delivery":
                pedido.direccion = cliente.direccion or "Sin direccion"
                pedido.repartidor = random.choice(repartidores) if random.random() > 0.2 else None
                pedido.costo_delivery = D("6.00")
            elif tipo == "mesa":
                pedido.mesa = str(random.randint(1, 12))
            pedido.save()

            # Crear fecha retroactiva
            fecha = timezone.now() - timedelta(days=hace, hours=random.randint(0, 8))
            Pedido.objects.filter(pk=pedido.pk).update(creado_en=fecha)

            n_items = random.randint(1, 3)
            for _ in range(n_items):
                if productos_pizza and random.random() > 0.4:
                    producto = random.choice(productos_pizza)
                    tamano = random.choice(tamano_lista)
                    cantidad = random.randint(1, 2)
                    detalle = DetallePedido(
                        pedido=pedido, producto=producto, tamano=tamano, cantidad=cantidad,
                        precio_unitario=producto.precio_para(tamano),
                    )
                    detalle.save()
                    if random.random() > 0.6 and extra_lista:
                        extra = random.choice(extra_lista)
                        DetalleExtra.objects.create(detalle=detalle, ingrediente=extra, precio=extra.precio_extra)
                        detalle.calcular()
                        detalle.save(update_fields=["subtotal_cache"])
                else:
                    producto = random.choice(productos_otros)
                    cantidad = random.randint(1, 2)
                    DetallePedido.objects.create(
                        pedido=pedido, producto=producto, cantidad=cantidad,
                        precio_unitario=producto.precio_base,
                    )

            # Estado y pago
            estado = random.choice(estados)
            pedido.estado = estado
            if estado == "entregado":
                pedido.entregado_en = fecha + timedelta(minutes=random.randint(20, 50))
            pedido.save()

            if estado in ("entregado", "en_camino", "listo") and random.random() > 0.15:
                monto = pedido.total if estado == "entregado" else (pedido.total / 2)
                pago = Pago.objects.create(
                    pedido=pedido, metodo=random.choice(metodos), usuario=admin,
                    monto=monto.quantize(D("0.10")),
                )
                Pago.objects.filter(pk=pago.pk).update(fecha_pago=fecha + timedelta(minutes=random.randint(10, 40)))
            creados += 1

        self.stdout.write(f"{creados} pedidos de ejemplo creados.")
