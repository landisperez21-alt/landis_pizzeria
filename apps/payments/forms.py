from django import forms

from apps.orders.models import Pedido

from .models import MetodoPago, Pago, SesionCaja


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["pedido", "metodo", "monto", "referencia_operacion", "observaciones"]
        widgets = {
            "pedido": forms.Select(attrs={"class": "form-select"}),
            "metodo": forms.Select(attrs={"class": "form-select"}),
            "monto": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "referencia_operacion": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pedido"].queryset = Pedido.objects.exclude(estado="cancelado").select_related("cliente")
        self.fields["metodo"].queryset = MetodoPago.objects.filter(activo=True)

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto


class SesionCajaForm(forms.ModelForm):
    class Meta:
        model = SesionCaja
        fields = ["monto_inicial", "observaciones"]
        widgets = {
            "monto_inicial": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "observaciones": forms.TextInput(attrs={"class": "form-control"}),
        }


class CierreCajaForm(forms.ModelForm):
    class Meta:
        model = SesionCaja
        fields = ["monto_final", "observaciones"]
        widgets = {
            "monto_final": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "observaciones": forms.TextInput(attrs={"class": "form-control"}),
        }
