from django.contrib.auth.views import LoginView
from django.urls import path

from . import views
from .forms import InicioSesionForm


app_name = "usuarios"


urlpatterns = [
    path(
        "registro/",
        views.registro,
        name="registro",
    ),

    path(
        "login/",
        LoginView.as_view(
            template_name="usuarios/login.html",
            authentication_form=InicioSesionForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path(
        "logout/",
        views.cerrar_sesion,
        name="logout",
    ),
]