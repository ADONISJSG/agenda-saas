from django.contrib import admin

from .models import (
    Especialidad,
    Profesional,
    Servicio,
)


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "activa",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "activa",
    )

    ordering = (
        "nombre",
    )


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo",
        "especialidad",
        "telefono",
        "correo",
        "activo",
    )

    search_fields = (
        "nombres",
        "apellidos",
        "telefono",
        "correo",
    )

    list_filter = (
        "activo",
        "especialidad",
    )

    ordering = (
        "apellidos",
        "nombres",
    )


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "especialidad",
        "duracion_minutos",
        "precio",
        "activo",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    list_filter = (
        "activo",
        "especialidad",
    )

    ordering = (
        "especialidad",
        "nombre",
    )

    list_editable = (
        "precio",
        "activo",
    )