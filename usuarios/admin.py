from django.contrib import admin

from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        "cedula",
        "nombre_completo",
        "celular",
        "correo",
        "creado_en",
    )

    search_fields = (
        "cedula",
        "nombres",
        "apellidos",
        "celular",
        "correo",
    )

    list_filter = (
        "creado_en",
    )

    ordering = (
        "apellidos",
        "nombres",
    )

    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )