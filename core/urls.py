from django.urls import path

from . import views


app_name = "core"


urlpatterns = [
    path(
        "",
        views.inicio,
        name="inicio",
    ),

    path(
        "panel/",
        views.panel,
        name="panel",
    ),

    path(
        "panel/citas/<uuid:codigo>/",
        views.detalle_cita,
        name="detalle_cita",
    ),

    path(
        "panel/citas/<uuid:codigo>/actualizar/",
        views.actualizar_cita,
        name="actualizar_cita",
    ),
]