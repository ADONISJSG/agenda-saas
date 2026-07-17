import re
from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from servicios.models import (
    BloqueoAgenda,
    Especialidad,
    HorarioProfesional,
    Profesional,
    Servicio,
)
from usuarios.models import Paciente

from .models import Cita


def normalizar_documento(documento):
    return re.sub(
        r"[^A-Za-z0-9]",
        "",
        documento,
    ).upper()


def normalizar_celular(celular):
    celular = celular.strip()

    tiene_prefijo = celular.startswith("+")

    numeros = re.sub(
        r"\D",
        "",
        celular,
    )

    if tiene_prefijo:
        return f"+{numeros}"

    return numeros


def validar_cedula_ecuatoriana(cedula):
    if not cedula.isdigit():
        return False

    if len(cedula) != 10:
        return False

    provincia = int(cedula[:2])
    tercer_digito = int(cedula[2])

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


def intervalos_se_superponen(
    inicio_uno,
    fin_uno,
    inicio_dos,
    fin_dos,
):
    return (
        inicio_uno < fin_dos
        and fin_uno > inicio_dos
    )


class AgendarCitaForm(forms.Form):
    nombres = forms.CharField(
        label="Nombres completos",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ejemplo: Luis Aníbal",
                "autocomplete": "given-name",
            }
        ),
    )

    apellidos = forms.CharField(
        label="Apellidos completos",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ejemplo: Carrillo Saltos",
                "autocomplete": "family-name",
            }
        ),
    )

    nacionalidad = forms.CharField(
        label="Nacionalidad",
        max_length=80,
        initial="Ecuador",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ejemplo: Ecuador",
                "autocomplete": "country-name",
            }
        ),
    )

    tipo_documento = forms.ChoiceField(
        label="Tipo de documento",
        choices=Paciente.TipoDocumento.choices,
    )

    cedula = forms.CharField(
        label="Número de documento",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Cédula, DNI o pasaporte"
                ),
                "autocomplete": "off",
            }
        ),
    )

    celular = forms.CharField(
        label="Celular",
        max_length=25,
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Ejemplo: +593991234567"
                ),
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
                "placeholder": "Opcional",
                "autocomplete": "email",
            }
        ),
    )

    especialidad = forms.ModelChoiceField(
        label="Especialidad",
        queryset=Especialidad.objects.none(),
        empty_label=None,
    )

    profesional = forms.ModelChoiceField(
        label="Profesional",
        queryset=Profesional.objects.none(),
        empty_label=None,
    )

    servicio = forms.ModelChoiceField(
        label="Servicio",
        queryset=Servicio.objects.none(),
        required=False,
        widget=forms.HiddenInput(),
    )

    fecha = forms.DateField(
        label="Fecha",
        widget=forms.HiddenInput(),
    )

    hora = forms.TimeField(
        label="Hora",
        input_formats=[
            "%H:%M",
            "%H:%M:%S",
        ],
        widget=forms.HiddenInput(),
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
        ].queryset = Especialidad.objects.filter(
            activa=True,
        )

        self.fields[
            "profesional"
        ].queryset = Profesional.objects.filter(
            activo=True,
            especialidad__activa=True,
        ).select_related(
            "especialidad",
        )

        self.fields[
            "servicio"
        ].queryset = Servicio.objects.filter(
            activo=True,
            especialidad__activa=True,
        ).select_related(
            "especialidad",
        )

    def clean_nombres(self):
        nombres = self.cleaned_data[
            "nombres"
        ].strip()

        if len(nombres) < 2:
            raise forms.ValidationError(
                "Ingresa los nombres completos."
            )

        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data[
            "apellidos"
        ].strip()

        if len(apellidos) < 2:
            raise forms.ValidationError(
                "Ingresa los apellidos completos."
            )

        return apellidos

    def clean_nacionalidad(self):
        nacionalidad = self.cleaned_data[
            "nacionalidad"
        ].strip()

        if len(nacionalidad) < 3:
            raise forms.ValidationError(
                "Ingresa una nacionalidad válida."
            )

        return nacionalidad.title()

    def clean_cedula(self):
        documento = normalizar_documento(
            self.cleaned_data["cedula"]
        )

        if len(documento) < 4:
            raise forms.ValidationError(
                (
                    "El número de documento debe "
                    "tener al menos 4 caracteres."
                )
            )

        if len(documento) > 30:
            raise forms.ValidationError(
                (
                    "El número de documento no puede "
                    "superar los 30 caracteres."
                )
            )

        return documento

    def clean_celular(self):
        celular = normalizar_celular(
            self.cleaned_data["celular"]
        )

        cantidad_digitos = len(
            re.sub(
                r"\D",
                "",
                celular,
            )
        )

        if (
            cantidad_digitos < 7
            or cantidad_digitos > 15
        ):
            raise forms.ValidationError(
                (
                    "Ingresa un número celular válido. "
                    "Puede incluir el código del país."
                )
            )

        return celular

    def clean_correo(self):
        correo = self.cleaned_data.get(
            "correo",
            "",
        )

        return correo.strip().lower()

    def clean_fecha(self):
        fecha = self.cleaned_data[
            "fecha"
        ]

        if fecha < timezone.localdate():
            raise forms.ValidationError(
                (
                    "La fecha seleccionada no puede "
                    "estar en el pasado."
                )
            )

        return fecha

    def clean(self):
        datos = super().clean()

        nacionalidad = datos.get(
            "nacionalidad"
        )

        tipo_documento = datos.get(
            "tipo_documento"
        )

        documento = datos.get(
            "cedula"
        )

        especialidad = datos.get(
            "especialidad"
        )

        profesional = datos.get(
            "profesional"
        )

        servicio = datos.get(
            "servicio"
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

        referencia_pago = datos.get(
            "referencia_pago",
            "",
        ).strip()

        if (
            nacionalidad
            and tipo_documento
            == Paciente.TipoDocumento.CEDULA
            and nacionalidad.lower()
            in {
                "ecuador",
                "ecuatoriana",
                "ecuatoriano",
            }
            and documento
            and not validar_cedula_ecuatoriana(
                documento
            )
        ):
            self.add_error(
                "cedula",
                (
                    "Ingresa una cédula "
                    "ecuatoriana válida."
                ),
            )

        if (
            profesional
            and especialidad
            and profesional.especialidad_id
            != especialidad.id
        ):
            self.add_error(
                "profesional",
                (
                    "El profesional seleccionado no "
                    "pertenece a esa especialidad."
                ),
            )

        if especialidad and not servicio:
            servicio = (
                Servicio.objects.filter(
                    especialidad=especialidad,
                    activo=True,
                )
                .order_by("id")
                .first()
            )

            if servicio:
                datos["servicio"] = servicio
            else:
                self.add_error(
                    "especialidad",
                    (
                        "La especialidad seleccionada "
                        "no tiene un servicio disponible."
                    ),
                )

        if (
            servicio
            and especialidad
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
            fecha
            and hora
            and fecha == timezone.localdate()
        ):
            hora_actual = (
                timezone.localtime()
                .replace(
                    tzinfo=None,
                )
                .time()
            )

            if hora <= hora_actual:
                self.add_error(
                    "hora",
                    (
                        "Selecciona una hora posterior "
                        "a la hora actual."
                    ),
                )

        if (
            profesional
            and servicio
            and fecha
            and hora
        ):
            self.validar_disponibilidad(
                profesional=profesional,
                servicio=servicio,
                fecha=fecha,
                hora=hora,
            )

        if (
            metodo_pago
            == Cita.MetodoPago.TRANSFERENCIA
            and not referencia_pago
        ):
            self.add_error(
                "referencia_pago",
                (
                    "Ingresa la referencia "
                    "de la transferencia."
                ),
            )

        datos["referencia_pago"] = (
            referencia_pago
        )

        return datos

    def validar_disponibilidad(
        self,
        profesional,
        servicio,
        fecha,
        hora,
    ):
        fecha_hora_inicio = datetime.combine(
            fecha,
            hora,
        )

        fecha_hora_fin = (
            fecha_hora_inicio
            + timedelta(
                minutes=servicio.duracion_minutos,
            )
        )

        horarios = (
            HorarioProfesional.objects.filter(
                profesional=profesional,
                dia_semana=fecha.weekday(),
                activo=True,
            )
            .order_by(
                "hora_inicio",
            )
        )

        if not horarios.exists():
            self.add_error(
                "fecha",
                (
                    "El profesional no atiende "
                    "en la fecha seleccionada."
                ),
            )

            return

        horario_valido = False

        for horario in horarios:
            inicio_jornada = datetime.combine(
                fecha,
                horario.hora_inicio,
            )

            fin_jornada = datetime.combine(
                fecha,
                horario.hora_fin,
            )

            diferencia = (
                fecha_hora_inicio
                - inicio_jornada
            ).total_seconds()

            coincide_intervalo = (
                diferencia >= 0
                and diferencia
                % (
                    horario.intervalo_minutos
                    * 60
                )
                == 0
            )

            cabe_en_jornada = (
                fecha_hora_inicio
                >= inicio_jornada
                and fecha_hora_fin
                <= fin_jornada
            )

            if (
                coincide_intervalo
                and cabe_en_jornada
            ):
                horario_valido = True
                break

        if not horario_valido:
            self.add_error(
                "hora",
                (
                    "La hora seleccionada no está "
                    "dentro del horario de atención."
                ),
            )

            return

        bloqueos = BloqueoAgenda.objects.filter(
            profesional=profesional,
            fecha=fecha,
            activo=True,
        )

        for bloqueo in bloqueos:
            if bloqueo.dia_completo:
                self.add_error(
                    "fecha",
                    (
                        "El profesional no está disponible "
                        "en esa fecha."
                    ),
                )

                return

            if (
                bloqueo.hora_inicio
                and bloqueo.hora_fin
            ):
                inicio_bloqueo = datetime.combine(
                    fecha,
                    bloqueo.hora_inicio,
                )

                fin_bloqueo = datetime.combine(
                    fecha,
                    bloqueo.hora_fin,
                )

                if intervalos_se_superponen(
                    fecha_hora_inicio,
                    fecha_hora_fin,
                    inicio_bloqueo,
                    fin_bloqueo,
                ):
                    self.add_error(
                        "hora",
                        (
                            "Ese horario se encuentra "
                            "separado o bloqueado."
                        ),
                    )

                    return

        citas_existentes = (
            Cita.objects.filter(
                profesional=profesional,
                fecha=fecha,
            )
            .exclude(
                estado=Cita.Estado.CANCELADA,
            )
            .select_related(
                "servicio",
            )
        )

        for cita in citas_existentes:
            inicio_cita = datetime.combine(
                fecha,
                cita.hora,
            )

            duracion_existente = (
                cita.servicio.duracion_minutos
                if cita.servicio_id
                else 30
            )

            fin_cita = (
                inicio_cita
                + timedelta(
                    minutes=duracion_existente,
                )
            )

            if intervalos_se_superponen(
                fecha_hora_inicio,
                fecha_hora_fin,
                inicio_cita,
                fin_cita,
            ):
                self.add_error(
                    "hora",
                    (
                        "Ese horario ya fue separado. "
                        "Selecciona otro disponible."
                    ),
                )

                return

    @transaction.atomic
    def save(self):
        datos = self.cleaned_data

        usuario, creado = (
            Paciente.objects.get_or_create(
                nacionalidad=datos[
                    "nacionalidad"
                ],
                tipo_documento=datos[
                    "tipo_documento"
                ],
                cedula=datos[
                    "cedula"
                ],
                defaults={
                    "nombres": datos[
                        "nombres"
                    ],
                    "apellidos": datos[
                        "apellidos"
                    ],
                    "celular": datos[
                        "celular"
                    ],
                    "correo": datos.get(
                        "correo",
                        "",
                    ),
                },
            )
        )

        if not creado:
            usuario.nombres = datos[
                "nombres"
            ]

            usuario.apellidos = datos[
                "apellidos"
            ]

            usuario.celular = datos[
                "celular"
            ]

            usuario.correo = datos.get(
                "correo",
                "",
            )

            usuario.save()

        cita = Cita(
            paciente=usuario,
            especialidad=datos[
                "especialidad"
            ],
            profesional=datos[
                "profesional"
            ],
            servicio=datos[
                "servicio"
            ],
            fecha=datos[
                "fecha"
            ],
            hora=datos[
                "hora"
            ],
            metodo_pago=datos[
                "metodo_pago"
            ],
            referencia_pago=datos.get(
                "referencia_pago",
                "",
            ),
        )

        cita.full_clean()
        cita.save()

        return cita