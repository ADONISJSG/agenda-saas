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
        "agendar/confirmacion/<uuid:codigo>/",
        views.confirmacion_cita,
        name="confirmacion",
    ),
]