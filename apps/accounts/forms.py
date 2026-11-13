from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Usuario", "autofocus": True}),
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contrasena"}),
    )


class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contrasena",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        help_text="Dejar en blanco para conservar la contrasena actual al editar.",
    )
    password2 = forms.CharField(
        label="Repetir contrasena",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "rol", "telefono", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-select"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 or p2:
            if p1 != p2:
                self.add_error("password2", "Las contrasenas no coinciden.")
            elif len(p1) < 8:
                self.add_error("password1", "La contrasena debe tener al menos 8 caracteres.")
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            usuario.set_password(password)
        if commit:
            usuario.save()
        return usuario


class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "telefono", "rol"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css)
        self.fields["rol"].widget.attrs["class"] = "form-select"
