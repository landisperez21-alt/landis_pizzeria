# PyMySQL se registra como MySQLdb para que Django pueda usar el driver MySQL.
import pymysql

pymysql.install_as_MySQLdb()

# ---------------------------------------------------------------------------
# Compatibilidad con MySQL 8.0 de XAMPP
# ---------------------------------------------------------------------------
# Django 6.1 declara como minimo MySQL 8.4, pero XAMPP distribuye MySQL 8.0.x.
# El backend MySQL de Django no usa caracteristicas exclusivas de 8.4, por lo
# que relajamos la verificacion de version para permitir 8.0 sin afectar al
# resto del entorno. Si actualizas a MySQL 8.4+ puedes eliminar este bloque.
from django.db.backends.mysql.features import DatabaseFeatures as _MySQLFeatures

_MySQLFeatures.minimum_database_version = (8, 0)
