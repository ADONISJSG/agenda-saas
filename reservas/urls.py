from django.urls import path

from . import views


app_name = "reservas"


urlpatterns = [
    path(
        "agendar/",
        views.agendar_cita,
        name="agendar",
    ),

    path(
        (
            "agendar/confirmacion/"
            "<uuid:codigo>/"
        ),
        views.confirmacion_cita,
        name="confirmacion",
    ),

    path(
        (
            "agendar/api/"
            "profesionales/"
        ),
        views.profesionales_por_especialidad,
        name="api_profesionales",
    ),

    path(
        (
            "agendar/api/"
            "disponibilidad-mensual/"
        ),
        views.disponibilidad_mensual,
        name="api_disponibilidad_mensual",
    ),

    path(
        (
            "agendar/api/"
            "horarios/"
        ),
        views.horarios_disponibles,
        name="api_horarios",
    ),
]   