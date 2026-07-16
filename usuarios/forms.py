from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ingresa tu nombre",
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ingresa tu apellido",
                "autocomplete": "family-name",
            }
        ),
    )

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "ejemplo@correo.com",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "Crea un nombre de usuario",
                "autocomplete": "username",
            }
        )

        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Crea una contraseña",
                "autocomplete": "new-password",
            }
        )

        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Repite la contraseña",
                "autocomplete": "new-password",
            }
        )

        self.fields["username"].help_text = (
            "Puedes usar letras, números y los caracteres @ . + - _"
        )

        self.fields["password1"].help_text = (
            "Usa mínimo 8 caracteres y evita una contraseña muy común."
        )

        self.fields["password2"].help_text = (
            "Escribe nuevamente la misma contraseña."
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este correo."
            )

        return email


class InicioSesionForm(AuthenticationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ingresa tu usuario",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Ingresa tu contraseña",
                "autocomplete": "current-password",
            }
        ),
    )