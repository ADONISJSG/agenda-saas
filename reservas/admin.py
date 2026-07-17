from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_corto",
        "paciente",
        "fecha",
        "hora",
        "especialidad",
        "profesional",
        "servicio",
        "anticipo",
        "estado_pago",
        "estado",
    )

    search_fields = (
        "codigo",
        "paciente__nombres",
        "paciente__apellidos",
        "paciente__cedula",
        "paciente__celular",
        "profesional__nombres",
        "profesional__apellidos",
        "referencia_pago",
    )

    list_filter = (
        "estado",
        "estado_pago",
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
        "estado_pago",
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
            "Información de la cita",
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
                    "estado_pago",
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

    @admin.display(description="Código")
    def codigo_corto(self, cita):
        return str(cita.codigo).split("-")[0].upper()