from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone


class AnuncioPropio(models.Model):
    titulo = models.CharField(
        max_length=150,
    )

    descripcion = models.CharField(
        max_length=250,
        blank=True,
    )

    imagen_url = models.URLField(
        verbose_name="URL de la imagen",
        help_text=(
            "Enlace público de la imagen publicitaria."
        ),
    )

    enlace = models.URLField(
        blank=True,
        help_text=(
            "Página que se abrirá al tocar el anuncio."
        ),
    )

    fecha_inicio = models.DateField(
        blank=True,
        null=True,
    )

    fecha_fin = models.DateField(
        blank=True,
        null=True,
    )

    orden = models.PositiveIntegerField(
        default=1,
    )

    activo = models.BooleanField(
        default=True,
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "orden",
            "-creado_en",
        ]

        verbose_name = "Publicidad propia"
        verbose_name_plural = "Publicidades propias"

    @property
    def vigente(self):
        hoy = timezone.localdate()

        if not self.activo:
            return False

        if (
            self.fecha_inicio
            and hoy < self.fecha_inicio
        ):
            return False

        if (
            self.fecha_fin
            and hoy > self.fecha_fin
        ):
            return False

        return True

    def __str__(self):
        return self.titulo


class Opinion(models.Model):
    nombre = models.CharField(
        max_length=150,
    )

    calificacion = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        default=5,
    )

    comentario = models.TextField(
        max_length=600,
    )

    aprobada = models.BooleanField(
        default=False,
    )

    destacada = models.BooleanField(
        default=False,
    )

    creada_en = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-destacada",
            "-creada_en",
        ]

        verbose_name = "Opinión"
        verbose_name_plural = "Opiniones"

    @property
    def estrellas(self):
        return "★" * self.calificacion

    def __str__(self):
        return (
            f"{self.nombre} - "
            f"{self.calificacion} estrellas"
        )