from django import forms

from .models import Categoria, Ingrediente, Producto, Tamano


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "orden", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
            "orden": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TamanoForm(forms.ModelForm):
    class Meta:
        model = Tamano
        fields = ["nombre", "porciones", "factor_precio", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "porciones": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "factor_precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ["nombre", "precio_extra", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "precio_extra": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["categoria", "nombre", "tipo", "descripcion", "precio_base", "imagen", "destacado", "activo"]
        widgets = {
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "precio_base": forms.NumberInput(attrs={"class": "form-control", "step": "0.10", "min": 0}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "destacado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
