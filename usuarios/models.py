from django.db import models


class Paciente(models.Model):

    class TipoDocumento(models.TextChoices):
        CEDULA = "CEDULA", "Cédula"
        DNI = "DNI", "DNI"
        PASAPORTE = "PASAPORTE", "Pasaporte"
        DOCUMENTO_IDENTIDAD = (
            "DOCUMENTO_IDENTIDAD",
            "Documento de identidad",
        )
        OTRO = "OTRO", "Otro"

    nombres = models.CharField(
        max_length=150,
    )

    apellidos = models.CharField(
        max_length=150,
    )

    nacionalidad = models.CharField(
        max_length=80,
        default="Ecuador",
    )

    tipo_documento = models.CharField(
        max_length=25,
        choices=TipoDocumento.choices,
        default=TipoDocumento.CEDULA,
    )

    cedula = models.CharField(
        verbose_name="Número de documento",
        max_length=30,
    )

    celular = models.CharField(
        max_length=25,
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

        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "nacionalidad",
                    "tipo_documento",
                    "cedula",
                ],
                name="documento_unico_por_nacionalidad",
            )
        ]

    @property
    def nombre_completo(self):
        return (
            f"{self.nombres} "
            f"{self.apellidos}"
        ).strip()

    @property
    def numero_documento(self):
        return self.cedula

    @property
    def documento_completo(self):
        return (
            f"{self.get_tipo_documento_display()}: "
            f"{self.cedula}"
        )

    def save(self, *args, **kwargs):
        self.nombres = self.nombres.strip()
        self.apellidos = self.apellidos.strip()
        self.nacionalidad = self.nacionalidad.strip()
        self.cedula = self.cedula.strip().upper()
        self.celular = self.celular.strip()
        self.correo = self.correo.strip().lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.nombre_completo} - "
            f"{self.cedula}"
        )