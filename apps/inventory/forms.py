from django import forms

from .models import Insumo, MovimientoInsumo


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ["codigo", "nombre", "unidad", "stock", "stock_minimo", "costo_unitario", "activo"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "unidad": forms.Select(attrs={"class": "form-select"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "min": 0}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "min": 0}),
            "costo_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MovimientoInsumoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInsumo
        fields = ["insumo", "tipo", "cantidad", "motivo"]
        widgets = {
            "insumo": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "step": "0.001", "min": 0}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["insumo"].queryset = Insumo.objects.filter(activo=True)

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return cantidad
