import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from servicios.models import (
    Especialidad,
    Profesional,
    Servicio,
)

from usuarios.models import Paciente


class Cita(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE_VERIFICACION = (
            "PENDIENTE_VERIFICACION",
            "Pendiente de verificación",
        )

        CONFIRMADA = (
            "CONFIRMADA",
            "Confirmada",
        )

        COMPLETADA = (
            "COMPLETADA",
            "Completada",
        )

        CANCELADA = (
            "CANCELADA",
            "Cancelada",
        )

    class MetodoPago(models.TextChoices):
        TRANSFERENCIA = (
            "TRANSFERENCIA",
            "Transferencia bancaria",
        )

        TARJETA = (
            "TARJETA",
            "Tarjeta de débito o crédito",
        )

    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="citas",
    )

    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name="citas",
    )

    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name="citas",
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="citas",
    )

    fecha = models.DateField()

    hora = models.TimeField()

    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
    )

    referencia_pago = models.CharField(
        max_length=120,
        blank=True,
        help_text=(
            "Número de comprobante o referencia "
            "de la transferencia."
        ),
    )

    valor_servicio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    anticipo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    saldo_pendiente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    estado = models.CharField(
        max_length=30,
        choices=Estado.choices,
        default=Estado.PENDIENTE_VERIFICACION,
    )

    creada_en = models.DateTimeField(
        auto_now_add=True,
    )

    actualizada_en = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "fecha",
            "hora",
        ]

        verbose_name = "Cita"
        verbose_name_plural = "Citas"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "profesional",
                    "fecha",
                    "hora",
                ],
                condition=~models.Q(
                    estado="CANCELADA",
                ),
                name="cita_unica_profesional_fecha_hora",
            )
        ]

    def clean(self):
        super().clean()

        if self.fecha and self.fecha < timezone.localdate():
            raise ValidationError(
                {
                    "fecha": (
                        "La fecha de la cita no puede "
                        "estar en el pasado."
                    )
                }
            )

        if (
            self.profesional_id
            and self.especialidad_id
            and self.profesional.especialidad_id
            != self.especialidad_id
        ):
            raise ValidationError(
                {
                    "profesional": (
                        "El profesional no pertenece "
                        "a la especialidad seleccionada."
                    )
                }
            )

        if (
            self.servicio_id
            and self.especialidad_id
            and self.servicio.especialidad_id
            != self.especialidad_id
        ):
            raise ValidationError(
                {
                    "servicio": (
                        "El servicio no pertenece "
                        "a la especialidad seleccionada."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.servicio_id:
            self.valor_servicio = self.servicio.precio

            self.anticipo = (
                self.valor_servicio
                * Decimal("0.20")
            ).quantize(
                Decimal("0.01")
            )

            self.saldo_pendiente = (
                self.valor_servicio
                - self.anticipo
            ).quantize(
                Decimal("0.01")
            )

        super().save(*args, **kwargs)

    def __str__(self):
        hora_texto = (
            self.hora.strftime("%H:%M")
            if self.hora
            else ""
        )

        return (
            f"{self.paciente.nombre_completo} - "
            f"{self.fecha} {hora_texto}"
        )