import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.http import require_GET

from core.models import (
    AnuncioPropio,
    Opinion,
)
from servicios.models import (
    BloqueoAgenda,
    Especialidad,
    HorarioProfesional,
    Profesional,
    Servicio,
)

from .forms import AgendarCitaForm
from .models import Cita


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


def obtener_servicio_principal(especialidad):
    return (
        Servicio.objects.filter(
            especialidad=especialidad,
            activo=True,
        )
        .order_by("id")
        .first()
    )


def obtener_horarios_profesional(profesional):
    return list(
        HorarioProfesional.objects.filter(
            profesional=profesional,
            activo=True,
        ).order_by(
            "dia_semana",
            "hora_inicio",
        )
    )


def obtener_bloqueos_profesional(
    profesional,
    fecha_inicio,
    fecha_fin,
):
    return list(
        BloqueoAgenda.objects.filter(
            profesional=profesional,
            fecha__range=(
                fecha_inicio,
                fecha_fin,
            ),
            activo=True,
        ).order_by(
            "fecha",
            "hora_inicio",
        )
    )


def obtener_citas_profesional(
    profesional,
    fecha_inicio,
    fecha_fin,
):
    return list(
        Cita.objects.filter(
            profesional=profesional,
            fecha__range=(
                fecha_inicio,
                fecha_fin,
            ),
        )
        .exclude(
            estado=Cita.Estado.CANCELADA,
        )
        .select_related(
            "servicio",
        )
        .order_by(
            "fecha",
            "hora",
        )
    )


def obtener_datos_transferencia(profesional):
    habilitada = (
        profesional.datos_transferencia_completos
    )

    if not habilitada:
        return {
            "habilitada": False,
            "banco": "",
            "tipo_cuenta": "",
            "numero_cuenta": "",
            "titular": "",
            "identificacion": "",
        }

    return {
        "habilitada": True,
        "banco": profesional.banco,
        "tipo_cuenta": (
            profesional.get_tipo_cuenta_display()
        ),
        "numero_cuenta": (
            profesional.numero_cuenta
        ),
        "titular": (
            profesional.titular_cuenta
        ),
        "identificacion": (
            profesional.identificacion_titular
        ),
    }


def obtener_horas_disponibles(
    profesional,
    servicio,
    fecha_seleccionada,
    horarios=None,
    bloqueos=None,
    citas=None,
):
    if horarios is None:
        horarios = obtener_horarios_profesional(
            profesional
        )

    if bloqueos is None:
        bloqueos = obtener_bloqueos_profesional(
            profesional,
            fecha_seleccionada,
            fecha_seleccionada,
        )

    if citas is None:
        citas = obtener_citas_profesional(
            profesional,
            fecha_seleccionada,
            fecha_seleccionada,
        )

    horarios_del_dia = [
        horario
        for horario in horarios
        if horario.dia_semana
        == fecha_seleccionada.weekday()
    ]

    if not horarios_del_dia:
        return []

    bloqueos_del_dia = [
        bloqueo
        for bloqueo in bloqueos
        if bloqueo.fecha == fecha_seleccionada
    ]

    if any(
        bloqueo.dia_completo
        for bloqueo in bloqueos_del_dia
    ):
        return []

    citas_del_dia = [
        cita
        for cita in citas
        if cita.fecha == fecha_seleccionada
    ]

    ahora = (
        timezone.localtime()
        .replace(
            tzinfo=None,
        )
    )

    horas_disponibles = set()

    for horario in horarios_del_dia:
        inicio_jornada = datetime.combine(
            fecha_seleccionada,
            horario.hora_inicio,
        )

        fin_jornada = datetime.combine(
            fecha_seleccionada,
            horario.hora_fin,
        )

        hora_actual = inicio_jornada

        while hora_actual < fin_jornada:
            fin_turno = (
                hora_actual
                + timedelta(
                    minutes=servicio.duracion_minutos,
                )
            )

            if fin_turno > fin_jornada:
                break

            if (
                fecha_seleccionada
                == timezone.localdate()
                and hora_actual <= ahora
            ):
                hora_actual += timedelta(
                    minutes=horario.intervalo_minutos,
                )

                continue

            bloqueada = False

            for bloqueo in bloqueos_del_dia:
                if (
                    bloqueo.dia_completo
                    or not bloqueo.hora_inicio
                    or not bloqueo.hora_fin
                ):
                    continue

                inicio_bloqueo = datetime.combine(
                    fecha_seleccionada,
                    bloqueo.hora_inicio,
                )

                fin_bloqueo = datetime.combine(
                    fecha_seleccionada,
                    bloqueo.hora_fin,
                )

                if intervalos_se_superponen(
                    hora_actual,
                    fin_turno,
                    inicio_bloqueo,
                    fin_bloqueo,
                ):
                    bloqueada = True
                    break

            if bloqueada:
                hora_actual += timedelta(
                    minutes=horario.intervalo_minutos,
                )

                continue

            ocupada = False

            for cita in citas_del_dia:
                inicio_cita = datetime.combine(
                    fecha_seleccionada,
                    cita.hora,
                )

                duracion_cita = (
                    cita.servicio.duracion_minutos
                    if cita.servicio_id
                    else 30
                )

                fin_cita = (
                    inicio_cita
                    + timedelta(
                        minutes=duracion_cita,
                    )
                )

                if intervalos_se_superponen(
                    hora_actual,
                    fin_turno,
                    inicio_cita,
                    fin_cita,
                ):
                    ocupada = True
                    break

            if not ocupada:
                horas_disponibles.add(
                    hora_actual.strftime(
                        "%H:%M"
                    )
                )

            hora_actual += timedelta(
                minutes=horario.intervalo_minutos,
            )

    return sorted(
        horas_disponibles
    )


def agendar_cita(request):
    if request.method == "POST":
        formulario = AgendarCitaForm(
            request.POST,
        )

        if formulario.is_valid():
            try:
                cita = formulario.save()

            except IntegrityError:
                formulario.add_error(
                    "hora",
                    (
                        "Ese horario acaba de ser "
                        "reservado por otra persona. "
                        "Selecciona otra hora."
                    ),
                )

            else:
                return redirect(
                    "reservas:confirmacion",
                    codigo=cita.codigo,
                )

    else:
        formulario = AgendarCitaForm()

    anuncios_activos = (
        AnuncioPropio.objects.filter(
            activo=True,
        )
        .order_by(
            "orden",
            "-creado_en",
        )
    )

    anuncios_vigentes = [
        anuncio
        for anuncio in anuncios_activos
        if anuncio.vigente
    ]

    opiniones = (
        Opinion.objects.filter(
            aprobada=True,
        )
        .order_by(
            "-destacada",
            "-creada_en",
        )[:6]
    )

    contexto = {
        "formulario": formulario,

        "especialidades": (
            Especialidad.objects.filter(
                activa=True,
            ).order_by(
                "nombre",
            )
        ),

        "profesionales": (
            Profesional.objects.filter(
                activo=True,
                especialidad__activa=True,
            )
            .select_related(
                "especialidad",
            )
            .order_by(
                "apellidos",
                "nombres",
            )
        ),

        "servicios": (
            Servicio.objects.filter(
                activo=True,
                especialidad__activa=True,
            )
            .select_related(
                "especialidad",
            )
            .order_by(
                "especialidad",
                "id",
            )
        ),

        "anuncios_propios": (
            anuncios_vigentes[:3]
        ),

        "opiniones": opiniones,
    }

    return render(
        request,
        "reservas/agendar.html",
        contexto,
    )


def confirmacion_cita(
    request,
    codigo,
):
    cita = get_object_or_404(
        Cita.objects.select_related(
            "paciente",
            "especialidad",
            "servicio",
            "profesional",
        ),
        codigo=codigo,
    )

    return render(
        request,
        "reservas/confirmacion.html",
        {
            "cita": cita,
        },
    )


@require_GET
def profesionales_por_especialidad(request):
    especialidad_id = request.GET.get(
        "especialidad_id"
    )

    if not especialidad_id:
        return JsonResponse(
            {
                "error": (
                    "Debes indicar una especialidad."
                )
            },
            status=400,
        )

    especialidad = get_object_or_404(
        Especialidad,
        id=especialidad_id,
        activa=True,
    )

    profesionales = (
        Profesional.objects.filter(
            especialidad=especialidad,
            activo=True,
        )
        .order_by(
            "apellidos",
            "nombres",
        )
    )

    datos = []

    for profesional in profesionales:
        iniciales = (
            f"{profesional.nombres[:1]}"
            f"{profesional.apellidos[:1]}"
        ).upper()

        datos.append(
            {
                "id": profesional.id,

                "nombre": (
                    profesional.nombre_completo
                ),

                "iniciales": iniciales,

                "especialidad": (
                    especialidad.nombre
                ),

                "transferencia": (
                    obtener_datos_transferencia(
                        profesional
                    )
                ),
            }
        )

    return JsonResponse(
        {
            "especialidad": {
                "id": especialidad.id,
                "nombre": especialidad.nombre,
            },

            "profesionales": datos,
        }
    )


@require_GET
def disponibilidad_mensual(request):
    profesional_id = request.GET.get(
        "profesional_id"
    )

    anio_texto = request.GET.get(
        "anio"
    )

    mes_texto = request.GET.get(
        "mes"
    )

    if not profesional_id:
        return JsonResponse(
            {
                "error": (
                    "Debes indicar un profesional."
                )
            },
            status=400,
        )

    hoy = timezone.localdate()

    try:
        anio = (
            int(anio_texto)
            if anio_texto
            else hoy.year
        )

        mes = (
            int(mes_texto)
            if mes_texto
            else hoy.month
        )

    except ValueError:
        return JsonResponse(
            {
                "error": (
                    "El año o el mes no son válidos."
                )
            },
            status=400,
        )

    if mes < 1 or mes > 12:
        return JsonResponse(
            {
                "error": (
                    "El mes debe estar entre 1 y 12."
                )
            },
            status=400,
        )

    profesional = get_object_or_404(
        Profesional.objects.select_related(
            "especialidad",
        ),
        id=profesional_id,
        activo=True,
    )

    servicio = obtener_servicio_principal(
        profesional.especialidad
    )

    if not servicio:
        return JsonResponse(
            {
                "error": (
                    "La especialidad del profesional "
                    "no tiene un servicio activo."
                )
            },
            status=400,
        )

    ultimo_dia = calendar.monthrange(
        anio,
        mes,
    )[1]

    fecha_inicio = date(
        anio,
        mes,
        1,
    )

    fecha_fin = date(
        anio,
        mes,
        ultimo_dia,
    )

    horarios = obtener_horarios_profesional(
        profesional
    )

    bloqueos = obtener_bloqueos_profesional(
        profesional,
        fecha_inicio,
        fecha_fin,
    )

    citas = obtener_citas_profesional(
        profesional,
        fecha_inicio,
        fecha_fin,
    )

    dias = []

    for numero_dia in range(
        1,
        ultimo_dia + 1,
    ):
        fecha_actual = date(
            anio,
            mes,
            numero_dia,
        )

        atiende_ese_dia = any(
            horario.dia_semana
            == fecha_actual.weekday()
            for horario in horarios
        )

        if fecha_actual < hoy:
            estado = "pasada"

        elif not atiende_ese_dia:
            estado = "sin_atencion"

        else:
            horas = obtener_horas_disponibles(
                profesional=profesional,
                servicio=servicio,
                fecha_seleccionada=fecha_actual,
                horarios=horarios,
                bloqueos=bloqueos,
                citas=citas,
            )

            if horas:
                estado = "disponible"
            else:
                estado = "separada"

        dias.append(
            {
                "fecha": (
                    fecha_actual.isoformat()
                ),

                "dia": numero_dia,

                "estado": estado,
            }
        )

    return JsonResponse(
        {
            "profesional": {
                "id": profesional.id,

                "nombre": (
                    profesional.nombre_completo
                ),
            },

            "mes": mes,

            "anio": anio,

            "primer_dia_semana": (
                fecha_inicio.weekday()
            ),

            "dias": dias,

            "leyenda": {
                "disponible": (
                    "Fecha disponible"
                ),

                "separada": (
                    "Fecha separada o sin cupos"
                ),

                "sin_atencion": (
                    "El profesional no atiende"
                ),

                "pasada": (
                    "Fecha anterior"
                ),
            },
        }
    )


@require_GET
def horarios_disponibles(request):
    profesional_id = request.GET.get(
        "profesional_id"
    )

    fecha_texto = request.GET.get(
        "fecha"
    )

    if not profesional_id or not fecha_texto:
        return JsonResponse(
            {
                "error": (
                    "Debes indicar el profesional "
                    "y la fecha."
                )
            },
            status=400,
        )

    try:
        fecha_seleccionada = (
            date.fromisoformat(
                fecha_texto
            )
        )

    except ValueError:
        return JsonResponse(
            {
                "error": (
                    "La fecha seleccionada "
                    "no es válida."
                )
            },
            status=400,
        )

    if (
        fecha_seleccionada
        < timezone.localdate()
    ):
        return JsonResponse(
            {
                "error": (
                    "La fecha no puede estar "
                    "en el pasado."
                )
            },
            status=400,
        )

    profesional = get_object_or_404(
        Profesional.objects.select_related(
            "especialidad",
        ),
        id=profesional_id,
        activo=True,
    )

    servicio = obtener_servicio_principal(
        profesional.especialidad
    )

    if not servicio:
        return JsonResponse(
            {
                "error": (
                    "No existe un servicio activo "
                    "para esta especialidad."
                )
            },
            status=400,
        )

    horas = obtener_horas_disponibles(
        profesional=profesional,
        servicio=servicio,
        fecha_seleccionada=fecha_seleccionada,
    )

    precio = servicio.precio

    anticipo = (
        precio
        * Decimal("0.20")
    ).quantize(
        Decimal("0.01")
    )

    saldo = (
        precio
        - anticipo
    ).quantize(
        Decimal("0.01")
    )

    return JsonResponse(
        {
            "fecha": (
                fecha_seleccionada.isoformat()
            ),

            "profesional": {
                "id": profesional.id,

                "nombre": (
                    profesional.nombre_completo
                ),

                "transferencia": (
                    obtener_datos_transferencia(
                        profesional
                    )
                ),
            },

            "servicio": {
                "id": servicio.id,

                "nombre": servicio.nombre,

                "duracion_minutos": (
                    servicio.duracion_minutos
                ),

                "precio": format(
                    precio,
                    ".2f",
                ),

                "anticipo": format(
                    anticipo,
                    ".2f",
                ),

                "saldo": format(
                    saldo,
                    ".2f",
                ),
            },

            "horas": horas,
        }
    )