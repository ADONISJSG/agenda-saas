from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "fecha",
        "hora",
        "especialidad",
        "profesional",
        "servicio",
        "anticipo",
        "estado",
    )

    search_fields = (
        "paciente__cedula",
        "paciente__nombres",
        "paciente__apellidos",
        "profesional__nombres",
        "profesional__apellidos",
        "referencia_pago",
    )

    list_filter = (
        "estado",
        "metodo_pago",
        "fecha",
        "especialidad",
        "profesional",
    )

    ordering = (
        "fecha",
        "hora",
    )

    list_editable = (
        "estado",
    )

    readonly_fields = (
        "codigo",
        "valor_servicio",
        "anticipo",
        "saldo_pendiente",
        "creada_en",
        "actualizada_en",
    )

    fieldsets = (
        (
            "Datos de la cita",
            {
                "fields": (
                    "codigo",
                    "paciente",
                    "especialidad",
                    "servicio",
                    "profesional",
                    "fecha",
                    "hora",
                    "estado",
                )
            },
        ),
        (
            "Información del pago",
            {
                "fields": (
                    "metodo_pago",
                    "referencia_pago",
                    "valor_servicio",
                    "anticipo",
                    "saldo_pendiente",
                )
            },
        ),
        (
            "Información del sistema",
            {
                "fields": (
                    "creada_en",
                    "actualizada_en",
                )
            },
        ),
    )