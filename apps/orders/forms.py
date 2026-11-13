from decimal import Decimal

from django import forms

from apps.catalog.models import Producto, Tamano
from apps.customers.models import Cliente, Repartidor

from .models import DetallePedido, Pedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente", "tipo", "mesa", "direccion", "repartidor", "costo_delivery", "descuento", "notas"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select", "id": "id_tipo"}),
            "mesa": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "repartidor": forms.Select(attrs={"class": "form-select"}),
            "costo_delivery": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "descuento": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(activo=True)
        self.fields["repartidor"].queryset = Repartidor.objects.filter(activo=True)
        self.fields["repartidor"].required = False
        self.fields["repartidor"].empty_label = "-- Sin asignar --"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("tipo") == Pedido.Tipo.DELIVERY and not cleaned.get("direccion"):
            self.add_error("direccion", "Indica la direccion para el delivery.")
        if cleaned.get("tipo") == Pedido.Tipo.MESA and not cleaned.get("mesa"):
            self.add_error("mesa", "Indica el numero o nombre de la mesa.")
        return cleaned


class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ["producto", "tamano", "cantidad", "notas"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-select", "id": "id_producto"}),
            "tamano": forms.Select(attrs={"class": "form-select", "id": "id_tamano"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": 1, "value": 1, "id": "id_cantidad"}),
            "notas": forms.TextInput(attrs={"class": "form-control", "placeholder": "Sin cebolla, extra queso..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.filter(activo=True).select_related("categoria")
        self.fields["tamano"].queryset = Tamano.objects.filter(activo=True)
        self.fields["tamano"].required = False
        self.fields["tamano"].empty_label = "-- Tamano (solo pizzas) --"

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad") or 1
        if cantidad < 1:
            raise forms.ValidationError("La cantidad debe ser al menos 1.")
        return cantidad
