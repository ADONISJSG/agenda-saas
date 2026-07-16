from django.db import IntegrityError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from servicios.models import (
    Especialidad,
    Profesional,
    Servicio,
)

from .forms import AgendarCitaForm
from .models import Cita


def agendar_cita(request):
    if request.method == "POST":
        formulario = AgendarCitaForm(
            request.POST,
        )

        if formulario.is_valid():
            try:
                cita = formulario.save()

            except IntegrityError:
                formulario.add_error(
                    "hora",
                    (
                        "Ese horario acaba de ser "
                        "reservado por otra persona. "
                        "Selecciona otro."
                    ),
                )

            else:
                return redirect(
                    "reservas:confirmacion",
                    codigo=cita.codigo,
                )

    else:
        formulario = AgendarCitaForm()

    contexto = {
        "formulario": formulario,

        "especialidades": (
            Especialidad.objects.filter(
                activa=True,
            )
        ),

        "servicios": (
            Servicio.objects.filter(
                activo=True,
                especialidad__activa=True,
            ).select_related(
                "especialidad",
            )
        ),

        "profesionales": (
            Profesional.objects.filter(
                activo=True,
                especialidad__activa=True,
            ).select_related(
                "especialidad",
            )
        ),
    }

    return render(
        request,
        "reservas/agendar.html",
        contexto,
    )


def confirmacion_cita(
    request,
    codigo,
):
    cita = get_object_or_404(
        Cita.objects.select_related(
            "paciente",
            "especialidad",
            "servicio",
            "profesional",
        ),
        codigo=codigo,
    )

    contexto = {
        "cita": cita,
    }

    return render(
        request,
        "reservas/confirmacion.html",
        contexto,
    )