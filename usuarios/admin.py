from django.contrib import admin

from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        "numero_documento_mostrado",
        "nombre_completo",
        "nacionalidad",
        "tipo_documento",
        "celular",
        "correo",
        "creado_en",
    )

    search_fields = (
        "nombres",
        "apellidos",
        "cedula",
        "celular",
        "correo",
        "nacionalidad",
    )

    list_filter = (
        "nacionalidad",
        "tipo_documento",
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

    fieldsets = (
        (
            "Información del usuario",
            {
                "fields": (
                    "nombres",
                    "apellidos",
                    "nacionalidad",
                    "tipo_documento",
                    "cedula",
                )
            },
        ),
        (
            "Información de contacto",
            {
                "fields": (
                    "celular",
                    "correo",
                )
            },
        ),
        (
            "Información del sistema",
            {
                "fields": (
                    "creado_en",
                    "actualizado_en",
                )
            },
        ),
    )

    @admin.display(
        description="Número de documento",
        ordering="cedula",
    )
    def numero_documento_mostrado(self, usuario):
        return usuario.cedula