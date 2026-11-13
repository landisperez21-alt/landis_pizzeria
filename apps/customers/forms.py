from django import forms

from apps.accounts.models import Usuario

from .models import Cliente, DireccionCliente, Repartidor


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "tipo_documento", "numero_documento", "telefono", "email", "direccion", "referencia", "notas", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_documento": forms.Select(attrs={"class": "form-select"}),
            "numero_documento": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "referencia": forms.TextInput(attrs={"class": "form-control"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        fields = ["cliente", "direccion", "referencia", "distrito", "principal", "activo"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "referencia": forms.TextInput(attrs={"class": "form-control"}),
            "distrito": forms.TextInput(attrs={"class": "form-control"}),
            "principal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RepartidorForm(forms.ModelForm):
    class Meta:
        model = Repartidor
        fields = ["usuario", "zona", "vehiculo", "placa", "disponible", "activo"]
        widgets = {
            "usuario": forms.Select(attrs={"class": "form-select"}),
            "zona": forms.TextInput(attrs={"class": "form-control"}),
            "vehiculo": forms.TextInput(attrs={"class": "form-control"}),
            "placa": forms.TextInput(attrs={"class": "form-control"}),
            "disponible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["usuario"].queryset = Usuario.objects.filter(rol=Usuario.Rol.REPARTIDOR)
