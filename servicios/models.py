from django.core.exceptions import ValidationError
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

    class TipoCuenta(models.TextChoices):
        AHORROS = (
            "AHORROS",
            "Cuenta de ahorros",
        )

        CORRIENTE = (
            "CORRIENTE",
            "Cuenta corriente",
        )

        OTRA = (
            "OTRA",
            "Otro tipo de cuenta",
        )

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
        max_length=25,
        blank=True,
    )

    correo = models.EmailField(
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    transferencia_habilitada = models.BooleanField(
        default=False,
        help_text=(
            "Permite que los usuarios paguen el anticipo "
            "mediante transferencia a este profesional."
        ),
    )

    banco = models.CharField(
        max_length=120,
        blank=True,
    )

    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TipoCuenta.choices,
        blank=True,
    )

    numero_cuenta = models.CharField(
        max_length=50,
        blank=True,
    )

    titular_cuenta = models.CharField(
        max_length=150,
        blank=True,
    )

    identificacion_titular = models.CharField(
        max_length=30,
        blank=True,
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
        return (
            f"{self.nombres} "
            f"{self.apellidos}"
        ).strip()

    @property
    def datos_transferencia_completos(self):
        return all(
            [
                self.transferencia_habilitada,
                self.banco,
                self.tipo_cuenta,
                self.numero_cuenta,
                self.titular_cuenta,
                self.identificacion_titular,
            ]
        )

    def clean(self):
        super().clean()

        if not self.transferencia_habilitada:
            return

        errores = {}

        campos_obligatorios = {
            "banco": "Ingresa el nombre del banco.",
            "tipo_cuenta": "Selecciona el tipo de cuenta.",
            "numero_cuenta": "Ingresa el número de cuenta.",
            "titular_cuenta": (
                "Ingresa el nombre del titular de la cuenta."
            ),
            "identificacion_titular": (
                "Ingresa la identificación del titular."
            ),
        }

        for campo, mensaje in campos_obligatorios.items():
            valor = getattr(self, campo, "")

            if not valor:
                errores[campo] = mensaje

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.nombres = self.nombres.strip()
        self.apellidos = self.apellidos.strip()
        self.telefono = self.telefono.strip()
        self.correo = self.correo.strip().lower()

        self.banco = self.banco.strip()
        self.numero_cuenta = self.numero_cuenta.strip()
        self.titular_cuenta = self.titular_cuenta.strip()
        self.identificacion_titular = (
            self.identificacion_titular
            .strip()
            .upper()
        )

        super().save(*args, **kwargs)

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
        return self.nombre


class HorarioProfesional(models.Model):

    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="horarios",
    )

    dia_semana = models.PositiveSmallIntegerField(
        choices=DiaSemana.choices,
    )

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    intervalo_minutos = models.PositiveIntegerField(
        default=30,
        help_text=(
            "Cantidad de minutos entre cada turno."
        ),
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "profesional",
            "dia_semana",
            "hora_inicio",
        ]

        verbose_name = "Horario de atención"
        verbose_name_plural = "Horarios de atención"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "profesional",
                    "dia_semana",
                    "hora_inicio",
                    "hora_fin",
                ],
                name="horario_unico_profesional",
            )
        ]

    def clean(self):
        super().clean()

        if (
            self.hora_inicio
            and self.hora_fin
            and self.hora_inicio >= self.hora_fin
        ):
            raise ValidationError(
                {
                    "hora_fin": (
                        "La hora final debe ser posterior "
                        "a la hora de inicio."
                    )
                }
            )

        if (
            self.intervalo_minutos
            and self.intervalo_minutos < 5
        ):
            raise ValidationError(
                {
                    "intervalo_minutos": (
                        "El intervalo debe ser de "
                        "al menos 5 minutos."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.profesional.nombre_completo} - "
            f"{self.get_dia_semana_display()} - "
            f"{self.hora_inicio.strftime('%H:%M')} a "
            f"{self.hora_fin.strftime('%H:%M')}"
        )


class BloqueoAgenda(models.Model):
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name="bloqueos_agenda",
    )

    fecha = models.DateField()

    dia_completo = models.BooleanField(
        default=True,
    )

    hora_inicio = models.TimeField(
        blank=True,
        null=True,
    )

    hora_fin = models.TimeField(
        blank=True,
        null=True,
    )

    motivo = models.CharField(
        max_length=200,
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "fecha",
            "hora_inicio",
        ]

        verbose_name = "Bloqueo de agenda"
        verbose_name_plural = "Bloqueos de agenda"

    def clean(self):
        super().clean()

        if self.dia_completo:
            self.hora_inicio = None
            self.hora_fin = None
            return

        if not self.hora_inicio or not self.hora_fin:
            raise ValidationError(
                (
                    "Para bloquear solo una parte del día, "
                    "debes indicar la hora inicial y final."
                )
            )

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                {
                    "hora_fin": (
                        "La hora final debe ser posterior "
                        "a la hora de inicio."
                    )
                }
            )

    def __str__(self):
        if self.dia_completo:
            horario = "Todo el día"
        else:
            horario = (
                f"{self.hora_inicio.strftime('%H:%M')} a "
                f"{self.hora_fin.strftime('%H:%M')}"
            )

        return (
            f"{self.profesional.nombre_completo} - "
            f"{self.fecha} - {horario}"
        )