from django.db import models


class Paciente(models.Model):
    nombres = models.CharField(
        max_length=150,
    )

    apellidos = models.CharField(
        max_length=150,
    )

    cedula = models.CharField(
        max_length=10,
        unique=True,
    )

    celular = models.CharField(
        max_length=10,
    )

    correo = models.EmailField(
        blank=True,
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "apellidos",
            "nombres",
        ]

        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    def __str__(self):
        return f"{self.nombre_completo} - {self.cedula}"