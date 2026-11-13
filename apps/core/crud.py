"""CRUD generico reutilizable basado en clases de configuracion.

Cada app declara una o varias instancias de `CrudConfig` y expone sus metodos
(`lista`, `crear`, `editar`, `alternar`, `eliminar`) directamente en `urls.py`.

Nota: los metodos NO se decoran con `@login_required` porque se invocan como
metodos enlazados (`config.lista`) desde `urls.py`; el decorador confundiria
`self` con `request`. La verificacion de sesion y de rol se hace dentro de cada
metodo.
"""
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import capfirst


def _resolver(obj, ruta):
    if callable(ruta):
        return ruta(obj)
    valor = obj
    for parte in str(ruta).split("."):
        valor = getattr(valor, parte, None)
        if valor is None:
            return ""
    return valor


class CrudConfig:
    def __init__(
        self,
        model,
        form_class,
        titulo,
        url_nombre,
        columnas,
        *,
        singular=None,
        campos_busqueda=(),
        campo_activo="activo",
        orden=None,
        permitir_crear=True,
        permitir_editar=True,
        permitir_alternar=True,
        roles=None,
        por_pagina=15,
        plantilla_lista="crud/lista.html",
        plantilla_form="crud/form.html",
        contexto_extra=None,
        exito_url=None,
    ):
        self.model = model
        self.form_class = form_class
        self.titulo = titulo
        self.singular = singular or titulo.rstrip("s")
        self.url_nombre = url_nombre
        self.columnas = columnas
        self.campos_busqueda = campos_busqueda
        self.campo_activo = campo_activo
        self.orden = orden
        self.permitir_crear = permitir_crear
        self.permitir_editar = permitir_editar
        self.permitir_alternar = permitir_alternar and campo_activo is not None
        self.roles = roles or ()
        self.por_pagina = por_pagina
        self.plantilla_lista = plantilla_lista
        self.plantilla_form = plantilla_form
        self.contexto_extra = contexto_extra
        self.exito_url = exito_url or url_nombre

    # -- utilidades internas -------------------------------------------------
    def _sin_sesion(self, request):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return None

    def _permitido(self, request):
        return not self.roles or request.user.rol in self.roles

    def _base_qs(self):
        qs = self.model.objects.all()
        if self.orden:
            qs = qs.order_by(*self.orden)
        return qs

    def _contexto_lista(self, request):
        q = request.GET.get("q", "").strip()
        qs = self._base_qs()
        if q and self.campos_busqueda:
            cond = Q()
            for campo in self.campos_busqueda:
                cond |= Q(**{f"{campo}__icontains": q})
            qs = qs.filter(cond)
        paginator = Paginator(qs, self.por_pagina)
        pagina = paginator.get_page(request.GET.get("page"))
        filas = []
        for obj in pagina.object_list:
            celdas = []
            for col in self.columnas:
                celdas.append({"tipo": col.get("tipo", "texto"), "valor": _resolver(obj, col["campo"]), "col": col})
            filas.append({"objeto": obj, "celdas": celdas})
        contexto = {
            "titulo": self.titulo,
            "singular": self.singular,
            "url_nombre": self.url_nombre,
            "columnas": self.columnas,
            "filas": filas,
            "pagina": pagina,
            "q": q,
            "permitir_crear": self.permitir_crear,
            "permitir_editar": self.permitir_editar,
            "permitir_alternar": self.permitir_alternar,
            "campo_activo": self.campo_activo,
        }
        if self.contexto_extra:
            contexto.update(self.contexto_extra(request))
        return contexto

    # -- vistas --------------------------------------------------------------
    def lista(self, request):
        sin_sesion = self._sin_sesion(request)
        if sin_sesion:
            return sin_sesion
        if not self._permitido(request):
            messages.error(request, "No tienes permisos para ver esta seccion.")
            return redirect("core:dashboard")
        return render(request, self.plantilla_lista, self._contexto_lista(request))

    def crear(self, request):
        sin_sesion = self._sin_sesion(request)
        if sin_sesion:
            return sin_sesion
        if not self._permitido(request) or not self.permitir_crear:
            messages.error(request, "No tienes permisos para crear en esta seccion.")
            return redirect("core:dashboard")
        form = self.form_class(request.POST or None, request.FILES or None)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, f"{self.singular} registrado correctamente.")
            return redirect(self.exito_url)
        return render(request, self.plantilla_form, {
            "titulo": f"Nuevo {self.singular.lower()}",
            "singular": self.singular,
            "url_nombre": self.url_nombre,
            "form": form,
        })

    def editar(self, request, pk):
        sin_sesion = self._sin_sesion(request)
        if sin_sesion:
            return sin_sesion
        if not self._permitido(request) or not self.permitir_editar:
            messages.error(request, "No tienes permisos para editar en esta seccion.")
            return redirect("core:dashboard")
        obj = get_object_or_404(self.model, pk=pk)
        form = self.form_class(request.POST or None, request.FILES or None, instance=obj)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, f"{self.singular} actualizado.")
            return redirect(self.exito_url)
        return render(request, self.plantilla_form, {
            "titulo": f"Editar {self.singular.lower()}",
            "singular": self.singular,
            "url_nombre": self.url_nombre,
            "form": form,
            "objeto": obj,
        })

    def alternar(self, request, pk):
        sin_sesion = self._sin_sesion(request)
        if sin_sesion:
            return sin_sesion
        if not self.permitir_alternar:
            return redirect(self.exito_url)
        if not self._permitido(request):
            messages.error(request, "No tienes permisos.")
            return redirect("core:dashboard")
        obj = get_object_or_404(self.model, pk=pk)
        if request.method == "POST":
            setattr(obj, self.campo_activo, not getattr(obj, self.campo_activo))
            obj.save(update_fields=[self.campo_activo])
            estado = "activado" if getattr(obj, self.campo_activo) else "desactivado"
            messages.success(request, f"{self.singular} {estado}.")
        return redirect(self.exito_url)

    def eliminar(self, request, pk):
        sin_sesion = self._sin_sesion(request)
        if sin_sesion:
            return sin_sesion
        if not self._permitido(request):
            messages.error(request, "No tienes permisos.")
            return redirect("core:dashboard")
        obj = get_object_or_404(self.model, pk=pk)
        if request.method == "POST":
            obj.delete()
            messages.success(request, f"{self.singular} eliminado.")
        return redirect(self.exito_url)

    # -- helpers de plantilla ------------------------------------------------
    def url_lista(self):
        return self.url_nombre

    def encabezados(self):
        return [capfirst(c["label"]) for c in self.columnas]
