from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import RegistroUsuarioForm


def registro(request):
    if request.user.is_authenticated:
        return redirect("core:panel")

    if request.method == "POST":
        formulario = RegistroUsuarioForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)

            return redirect("core:panel")
    else:
        formulario = RegistroUsuarioForm()

    contexto = {
        "formulario": formulario,
    }

    return render(
        request,
        "usuarios/registro.html",
        contexto,
    )


@require_POST
def cerrar_sesion(request):
    logout(request)

    return redirect("core:inicio")