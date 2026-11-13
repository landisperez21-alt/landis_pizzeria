# Pizzeria Don Landinis

Sistema web de gestion para una pizzeria con pedidos, delivery, caja, inventario y
reportes. Desarrollado con **Django** y **MySQL**.

## Modulos

| Modulo | Descripcion |
| --- | --- |
| Pedidos y delivery | Registro de pedidos, detalle con tamanos e ingredientes extra, flujo de estados y comanda para impresion. |
| Carta | Categorias, tamanos, ingredientes extra, productos, combos y recetas (insumos por producto). |
| Clientes y repartidores | Clientes con direcciones y repartidores con zona y vehiculo. |
| Pagos y caja | Metodos de pago, cobros totales/parciales, sesiones de caja (apertura y cierre). |
| Inventario de insumos | Insumos con stock y stock minimo, movimientos de entrada/salida/ajuste y descuento automatico por receta. |
| Dashboard y reportes | Indicadores del dia, graficos de ventas y pedidos, reportes por rango de fechas. |
| Usuarios y roles | Roles administrador, cajero, cocinero y repartidor con permisos por seccion. |

## Requisitos

- Python 3.11 o superior (probado con 3.14).
- MySQL 8 (XAMPP) o SQLite para pruebas.
- Las dependencias de `requirements.txt`.

## Puesta en marcha

```powershell
# 1. Crear y activar un entorno virtual (opcional pero recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear la base de datos en MySQL
#    (desde phpMyAdmin o la consola de MySQL)
#    CREATE DATABASE donlandinis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 4. Configurar credenciales de la base de datos
Copy-Item .env.example .env
#    y editar DB_USER / DB_PASSWORD con los datos de tu MySQL

# 5. Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Cargar datos de demostracion (incluye el usuario admin)
python manage.py datos_demo

# 7. Ejecutar el servidor
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/> e ingresar con:

| Rol | Usuario | Contrasena |
| --- | --- | --- |
| Administrador | `admin` | `DonLandinis2026` |
| Cajero | `cajero` | `Cajero2026` |
| Cocinero | `cocinero` | `Cocina2026` |
| Repartidor | `repartidor` | `Reparto2026` |

> El panel de administracion de Django esta disponible en `/admin/`.

## Uso rapido de SQLite (sin MySQL)

Define la variable de entorno antes de migrar:

```powershell
$env:DB_ENGINE = "sqlite"
python manage.py migrate
python manage.py datos_demo
python manage.py runserver
```

## Configuracion

Variables de entorno soportadas (ver `.env.example`):

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `DB_ENGINE` (`mysql` por defecto, o `sqlite`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

## Estructura

```
config/            Configuracion del proyecto (settings, urls, wsgi/asgi)
apps/
  core/            Dashboard, reportes, CRUD generico, mixins y datos demo
  accounts/        Usuario con roles y autenticacion
  catalog/         Carta: categorias, tamanos, ingredientes, productos, recetas
  customers/       Clientes, direcciones y repartidores
  orders/          Pedidos, detalle, extras, estados y comanda
  payments/        Metodos de pago, pagos y sesiones de caja
  inventory/       Insumos y movimientos de inventario
templates/         Plantillas HTML (layout, CRUD y modulos)
static/            CSS, JS, logo e iconos
```

## Notas tecnicas

- El driver MySQL es **PyMySQL** (puro Python), registrado como `MySQLdb` en
  `config/__init__.py`, por lo que no requiere compilar `mysqlclient`.
- El CRUD de los modulos de gestion reutiliza la clase `CrudConfig`
  (`apps/core/crud.py`) para evitar repetir vistas.
- Al marcar un pedido como **entregado** se descuentan automaticamente los
  insumos definidos en la receta de cada producto.
