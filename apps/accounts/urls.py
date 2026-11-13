from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("ingresar/", views.IngresarView.as_view(), name="login"),
    path("salir/", views.SalirView.as_view(), name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("usuarios/", views.lista, name="lista"),
    path("usuarios/nuevo/", views.crear, name="crear"),
    path("usuarios/<int:pk>/editar/", views.editar, name="editar"),
    path("usuarios/<int:pk>/alternar/", views.alternar_activo, name="alternar"),
]
