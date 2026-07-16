from datetime import datetime, timedelta
import re

from django import forms
from django.db import transaction
from django.utils import timezone

from servicios.models import (
    Especialidad,
    Profesional,
    Servicio,
)

from usuarios.models import Paciente

from .models import Cita


def generar_horas_disponibles():
    horas = []

    hora_actual = datetime.strptime(
        "08:00",
        "%H:%M",
    )

    hora_final = datetime.strptime(
        "18:00",
        "%H:%M",
    )

    while hora_actual <= hora_final:
        hora_texto = hora_actual.strftime(
            "%H:%M"
        )

        horas.append(
            (
                hora_texto,
                hora_texto,
            )
        )

        hora_actual += timedelta(
            minutes=30,
        )

    return horas


def validar_cedula_ecuatoriana(cedula):
    if not cedula.isdigit():
        return False

    if len(cedula) != 10:
        return False

    provincia = int(
        cedula[:2]
    )

    tercer_digito = int(
        cedula[2]
    )

    if provincia < 1 or provincia > 24:
        return False

    if tercer_digito >= 6:
        return False

    coeficientes = [
        2,
        1,
        2,
        1,
        2,
        1,
        2,
        1,
        2,
    ]

    suma = 0

    for indice, coeficiente in enumerate(
        coeficientes
    ):
        resultado = (
            int(cedula[indice])
            * coeficiente
        )

        if resultado >= 10:
            resultado -= 9

        suma += resultado

    digito_verificador = (
        10 - suma % 10
    ) % 10

    return (
        digito_verificador
        == int(cedula[-1])
    )


class AgendarCitaForm(forms.Form):
    nombres = forms.CharField(
        label="Nombres completos",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ejemplo: María Fernanda"
                ),
                "autocomplete": "given-name",
            }
        ),
    )

    apellidos = forms.CharField(
        label="Apellidos completos",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ejemplo: Zambrano López"
                ),
                "autocomplete": "family-name",
            }
        ),
    )

    cedula = forms.CharField(
        label="Cédula",
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "placeholder": "10 dígitos",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    celular = forms.CharField(
        label="Celular",
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "placeholder": "09XXXXXXXX",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )

    correo = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": (
                    "Opcional"
                ),
                "autocomplete": "email",
            }
        ),
    )

    especialidad = forms.ModelChoiceField(
        label="Especialidad",
        queryset=Especialidad.objects.none(),
        empty_label="Selecciona una especialidad",
    )

    servicio = forms.ModelChoiceField(
        label="Servicio",
        queryset=Servicio.objects.none(),
        empty_label="Selecciona un servicio",
    )

    profesional = forms.ModelChoiceField(
        label="Profesional",
        queryset=Profesional.objects.none(),
        empty_label="Selecciona un profesional",
    )

    fecha = forms.DateField(
        label="Fecha de la cita",
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )

    hora = forms.ChoiceField(
        label="Hora de la cita",
        choices=generar_horas_disponibles,
    )

    metodo_pago = forms.ChoiceField(
        label="Método de pago",
        choices=Cita.MetodoPago.choices,
        widget=forms.RadioSelect,
    )

    referencia_pago = forms.CharField(
        label="Referencia de transferencia",
        required=False,
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Número de comprobante o referencia"
                ),
            }
        ),
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "especialidad"
        ].queryset = (
            Especialidad.objects.filter(
                activa=True,
            )
        )

        self.fields[
            "servicio"
        ].queryset = (
            Servicio.objects.filter(
                activo=True,
                especialidad__activa=True,
            ).select_related(
                "especialidad",
            )
        )

        self.fields[
            "profesional"
        ].queryset = (
            Profesional.objects.filter(
                activo=True,
                especialidad__activa=True,
            ).select_related(
                "especialidad",
            )
        )

        self.fields[
            "fecha"
        ].widget.attrs["min"] = (
            timezone.localdate().isoformat()
        )

    def clean_cedula(self):
        cedula = (
            self.cleaned_data[
                "cedula"
            ]
            .strip()
        )

        if not validar_cedula_ecuatoriana(
            cedula
        ):
            raise forms.ValidationError(
                (
                    "Ingresa una cédula "
                    "ecuatoriana válida."
                )
            )

        return cedula

    def clean_celular(self):
        celular = re.sub(
            r"\D",
            "",
            self.cleaned_data[
                "celular"
            ],
        )

        if not re.fullmatch(
            r"09\d{8}",
            celular,
        ):
            raise forms.ValidationError(
                (
                    "Ingresa un celular "
                    "ecuatoriano válido "
                    "de 10 dígitos."
                )
            )

        return celular

    def clean_fecha(self):
        fecha = self.cleaned_data[
            "fecha"
        ]

        if fecha < timezone.localdate():
            raise forms.ValidationError(
                (
                    "La fecha no puede "
                    "estar en el pasado."
                )
            )

        return fecha

    def clean(self):
        datos = super().clean()

        especialidad = datos.get(
            "especialidad"
        )

        servicio = datos.get(
            "servicio"
        )

        profesional = datos.get(
            "profesional"
        )

        fecha = datos.get(
            "fecha"
        )

        hora = datos.get(
            "hora"
        )

        metodo_pago = datos.get(
            "metodo_pago"
        )

        referencia_pago = (
            datos.get(
                "referencia_pago",
                "",
            )
            .strip()
        )

        if (
            especialidad
            and servicio
            and servicio.especialidad_id
            != especialidad.id
        ):
            self.add_error(
                "servicio",
                (
                    "El servicio no pertenece "
                    "a la especialidad seleccionada."
                ),
            )

        if (
            especialidad
            and profesional
            and profesional.especialidad_id
            != especialidad.id
        ):
            self.add_error(
                "profesional",
                (
                    "El profesional no pertenece "
                    "a la especialidad seleccionada."
                ),
            )

        if (
            profesional
            and fecha
            and hora
        ):
            horario_ocupado = (
                Cita.objects.filter(
                    profesional=profesional,
                    fecha=fecha,
                    hora=hora,
                )
                .exclude(
                    estado=Cita.Estado.CANCELADA,
                )
                .exists()
            )

            if horario_ocupado:
                self.add_error(
                    "hora",
                    (
                        "Ese horario ya fue reservado. "
                        "Selecciona otra hora."
                    ),
                )

        if (
            metodo_pago
            == Cita.MetodoPago.TRANSFERENCIA
            and not referencia_pago
        ):
            self.add_error(
                "referencia_pago",
                (
                    "Ingresa el número o referencia "
                    "de la transferencia."
                ),
            )

        return datos

    @transaction.atomic
    def save(self):
        datos = self.cleaned_data

        paciente, creado = (
            Paciente.objects.get_or_create(
                cedula=datos["cedula"],
                defaults={
                    "nombres": (
                        datos["nombres"]
                        .strip()
                    ),
                    "apellidos": (
                        datos["apellidos"]
                        .strip()
                    ),
                    "celular": (
                        datos["celular"]
                    ),
                    "correo": (
                        datos.get(
                            "correo",
                            "",
                        )
                        .strip()
                        .lower()
                    ),
                },
            )
        )

        if not creado:
            paciente.nombres = (
                datos["nombres"]
                .strip()
            )

            paciente.apellidos = (
                datos["apellidos"]
                .strip()
            )

            paciente.celular = (
                datos["celular"]
            )

            paciente.correo = (
                datos.get(
                    "correo",
                    "",
                )
                .strip()
                .lower()
            )

            paciente.save()

        cita = Cita(
            paciente=paciente,
            especialidad=(
                datos["especialidad"]
            ),
            servicio=(
                datos["servicio"]
            ),
            profesional=(
                datos["profesional"]
            ),
            fecha=datos["fecha"],
            hora=datos["hora"],
            metodo_pago=(
                datos["metodo_pago"]
            ),
            referencia_pago=(
                datos.get(
                    "referencia_pago",
                    "",
                )
                .strip()
            ),
        )

        cita.full_clean()
        cita.save()

        return cita