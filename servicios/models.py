from django.db import models


class Especialidad(models.Model):
    nombre = models.CharField(
        max_length=120,
        unique=True,
    )

    descripcion = models.TextField(
        blank=True,
    )

    activa = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "nombre",
        ]

        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.nombre


class Profesional(models.Model):
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name="profesionales",
    )

    nombres = models.CharField(
        max_length=120,
    )

    apellidos = models.CharField(
        max_length=120,
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
    )

    correo = models.EmailField(
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "apellidos",
            "nombres",
        ]

        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    def __str__(self):
        return (
            f"{self.nombre_completo} - "
            f"{self.especialidad.nombre}"
        )


class Servicio(models.Model):
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name="servicios",
    )

    nombre = models.CharField(
        max_length=150,
    )

    descripcion = models.TextField(
        blank=True,
    )

    duracion_minutos = models.PositiveIntegerField(
        default=60,
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "especialidad__nombre",
            "nombre",
        ]

        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "especialidad",
                    "nombre",
                ],
                name="servicio_unico_por_especialidad",
            )
        ]

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"