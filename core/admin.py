from django.contrib import admin

from .models import (
    AnuncioPropio,
    Opinion,
)


@admin.register(AnuncioPropio)
class AnuncioPropioAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "orden",
        "fecha_inicio",
        "fecha_fin",
        "esta_vigente",
        "activo",
    )

    search_fields = (
        "titulo",
        "descripcion",
    )

    list_filter = (
        "activo",
        "fecha_inicio",
        "fecha_fin",
    )

    ordering = (
        "orden",
        "-creado_en",
    )

    list_editable = (
        "orden",
        "activo",
    )

    readonly_fields = (
        "creado_en",
    )

    fieldsets = (
        (
            "Contenido de la publicidad",
            {
                "fields": (
                    "titulo",
                    "descripcion",
                    "imagen_url",
                    "enlace",
                )
            },
        ),
        (
            "Publicación",
            {
                "fields": (
                    "fecha_inicio",
                    "fecha_fin",
                    "orden",
                    "activo",
                )
            },
        ),
        (
            "Información del sistema",
            {
                "fields": (
                    "creado_en",
                )
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Vigente",
    )
    def esta_vigente(self, anuncio):
        return anuncio.vigente


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "calificacion",
        "comentario_corto",
        "aprobada",
        "destacada",
        "creada_en",
    )

    search_fields = (
        "nombre",
        "comentario",
    )

    list_filter = (
        "aprobada",
        "destacada",
        "calificacion",
        "creada_en",
    )

    ordering = (
        "-destacada",
        "-creada_en",
    )

    list_editable = (
        "aprobada",
        "destacada",
    )

    readonly_fields = (
        "creada_en",
    )

    actions = (
        "aprobar_opiniones",
        "rechazar_opiniones",
        "marcar_destacadas",
    )

    @admin.display(description="Comentario")
    def comentario_corto(self, opinion):
        if len(opinion.comentario) <= 60:
            return opinion.comentario

        return f"{opinion.comentario[:60]}..."

    @admin.action(description="Aprobar opiniones seleccionadas")
    def aprobar_opiniones(self, request, queryset):
        queryset.update(aprobada=True)

    @admin.action(description="Ocultar opiniones seleccionadas")
    def rechazar_opiniones(self, request, queryset):
        queryset.update(aprobada=False)

    @admin.action(description="Marcar como destacadas")
    def marcar_destacadas(self, request, queryset):
        queryset.update(
            aprobada=True,
            destacada=True,
        )