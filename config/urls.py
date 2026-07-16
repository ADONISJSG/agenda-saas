from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "cuenta/",
        include("usuarios.urls"),
    ),

    path(
        "",
        include("reservas.urls"),
    ),

    path(
        "",
        include("core.urls"),
    ),
]