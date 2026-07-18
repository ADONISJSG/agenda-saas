from django.contrib import admin

from .models import (
    BloqueoAgenda,
    Especialidad,
    HorarioProfesional,
    Profesional,
    Servicio,
)


class HorarioProfesionalInline(admin.TabularInline):
    model = HorarioProfesional
    extra = 1

    fields = (
        "dia_semana",
        "hora_inicio",
        "hora_fin",
        "intervalo_minutos",
        "activo",
    )


class BloqueoAgendaInline(admin.TabularInline):
    model = BloqueoAgenda
    extra = 0

    fields = (
        "fecha",
        "dia_completo",
        "hora_inicio",
        "hora_fin",
        "motivo",
        "activo",
    )


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "cantidad_profesionales",
        "cantidad_servicios",
        "activa",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    list_filter = (
        "activa",
    )

    ordering = (
        "nombre",
    )

    list_editable = (
        "activa",
    )

    @admin.display(description="Profesionales")
    def cantidad_profesionales(self, especialidad):
        return especialidad.profesionales.count()

    @admin.display(description="Servicios")
    def cantidad_servicios(self, especialidad):
        return especialidad.servicios.count()


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo",
        "especialidad",
        "telefono",
        "transferencia_habilitada",
        "banco",
        "activo",
    )

    search_fields = (
        "nombres",
        "apellidos",
        "telefono",
        "correo",
        "especialidad__nombre",
        "banco",
        "numero_cuenta",
        "titular_cuenta",
        "identificacion_titular",
    )

    list_filter = (
        "activo",
        "transferencia_habilitada",
        "especialidad",
        "banco",
    )

    ordering = (
        "apellidos",
        "nombres",
    )

    list_editable = (
        "transferencia_habilitada",
        "activo",
    )

    inlines = (
        HorarioProfesionalInline,
        BloqueoAgendaInline,
    )

    fieldsets = (
        (
            "Información del profesional",
            {
                "fields": (
                    "nombres",
                    "apellidos",
                    "especialidad",
                )
            },
        ),
        (
            "Información de contacto",
            {
                "fields": (
                    "telefono",
                    "correo",
                )
            },
        ),
        (
            "Datos para transferencias",
            {
                "description": (
                    "Estos datos aparecerán únicamente "
                    "cuando el usuario seleccione transferencia."
                ),
                "fields": (
                    "transferencia_habilitada",
                    "banco",
                    "tipo_cuenta",
                    "numero_cuenta",
                    "titular_cuenta",
                    "identificacion_titular",
                ),
            },
        ),
        (
            "Estado",
            {
                "fields": (
                    "activo",
                )
            },
        ),
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
        "especialidad__nombre",
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


@admin.register(HorarioProfesional)
class HorarioProfesionalAdmin(admin.ModelAdmin):
    list_display = (
        "profesional",
        "dia_semana",
        "hora_inicio",
        "hora_fin",
        "intervalo_minutos",
        "activo",
    )

    search_fields = (
        "profesional__nombres",
        "profesional__apellidos",
    )

    list_filter = (
        "activo",
        "dia_semana",
        "profesional",
    )

    ordering = (
        "profesional",
        "dia_semana",
        "hora_inicio",
    )

    list_editable = (
        "activo",
    )


@admin.register(BloqueoAgenda)
class BloqueoAgendaAdmin(admin.ModelAdmin):
    list_display = (
        "profesional",
        "fecha",
        "tipo_bloqueo",
        "motivo",
        "activo",
    )

    search_fields = (
        "profesional__nombres",
        "profesional__apellidos",
        "motivo",
    )

    list_filter = (
        "activo",
        "dia_completo",
        "fecha",
        "profesional",
    )

    ordering = (
        "fecha",
        "hora_inicio",
    )

    list_editable = (
        "activo",
    )

    @admin.display(description="Horario bloqueado")
    def tipo_bloqueo(self, bloqueo):
        if bloqueo.dia_completo:
            return "Todo el día"

        if bloqueo.hora_inicio and bloqueo.hora_fin:
            return (
                f"{bloqueo.hora_inicio.strftime('%H:%M')} "
                f"a {bloqueo.hora_fin.strftime('%H:%M')}"
            )

        return "Sin horario"