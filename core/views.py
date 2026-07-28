import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import (
    staff_member_required,
)
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET

from reservas.models import Cita
from servicios.models import (
    BloqueoAgenda,
    HorarioProfesional,
)
from usuarios.models import Paciente


def inicio(request):
    return render(
        request,
        "core/inicio.html",
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


def parsear_hora(hora_texto):
    formatos = [
        "%H:%M",
        "%H:%M:%S",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(
                hora_texto,
                formato,
            ).time()

        except ValueError:
            continue

    return None


def obtener_horas_reprogramacion(
    cita,
    fecha_seleccionada,
):
    horarios = list(
        HorarioProfesional.objects.filter(
            profesional=cita.profesional,
            dia_semana=fecha_seleccionada.weekday(),
            activo=True,
        ).order_by(
            "hora_inicio",
        )
    )

    if not horarios:
        return []

    bloqueos = list(
        BloqueoAgenda.objects.filter(
            profesional=cita.profesional,
            fecha=fecha_seleccionada,
            activo=True,
        ).order_by(
            "hora_inicio",
        )
    )

    if any(
        bloqueo.dia_completo
        for bloqueo in bloqueos
    ):
        return []

    citas_existentes = list(
        Cita.objects.filter(
            profesional=cita.profesional,
            fecha=fecha_seleccionada,
        )
        .exclude(
            pk=cita.pk,
        )
        .exclude(
            estado=Cita.Estado.CANCELADA,
        )
        .select_related(
            "servicio",
        )
        .order_by(
            "hora",
        )
    )

    ahora = (
        timezone.localtime()
        .replace(
            tzinfo=None,
        )
    )

    horas_disponibles = set()

    for horario in horarios:
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
                    minutes=(
                        cita.servicio.duracion_minutos
                    ),
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
                    minutes=(
                        horario.intervalo_minutos
                    ),
                )

                continue

            bloqueada = False

            for bloqueo in bloqueos:
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
                    minutes=(
                        horario.intervalo_minutos
                    ),
                )

                continue

            ocupada = False

            for cita_existente in citas_existentes:
                inicio_cita = datetime.combine(
                    fecha_seleccionada,
                    cita_existente.hora,
                )

                duracion_existente = (
                    cita_existente.servicio.duracion_minutos
                    if cita_existente.servicio_id
                    else 30
                )

                fin_cita = (
                    inicio_cita
                    + timedelta(
                        minutes=duracion_existente,
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
                minutes=(
                    horario.intervalo_minutos
                ),
            )

    return sorted(
        horas_disponibles
    )


@staff_member_required(
    login_url="usuarios:login",
)
def panel(request):
    hoy = timezone.localdate()

    nombre_completo = (
        request.user.get_full_name().strip()
    )

    nombre_usuario = (
        nombre_completo
        if nombre_completo
        else request.user.username
    )

    partes_nombre = nombre_usuario.split()

    iniciales = "".join(
        parte[0]
        for parte in partes_nombre[:2]
        if parte
    ).upper()

    citas_base = Cita.objects.select_related(
        "paciente",
        "especialidad",
        "servicio",
        "profesional",
    )

    citas_hoy = (
        citas_base.filter(
            fecha=hoy,
        )
        .exclude(
            estado=Cita.Estado.CANCELADA,
        )
        .order_by(
            "hora",
        )
    )

    proximas_citas = (
        citas_base.filter(
            fecha__gte=hoy,
        )
        .exclude(
            estado=Cita.Estado.CANCELADA,
        )
        .order_by(
            "fecha",
            "hora",
        )[:6]
    )

    total_usuarios = Paciente.objects.count()

    total_citas_hoy = citas_hoy.count()

    pagos_pendientes = (
        citas_base.filter(
            estado_pago=Cita.EstadoPago.PENDIENTE,
        )
        .exclude(
            estado=Cita.Estado.CANCELADA,
        )
        .count()
    )

    citas_confirmadas = citas_base.filter(
        estado=Cita.Estado.CONFIRMADA,
    ).count()

    citas_pendientes = citas_base.filter(
        estado=(
            Cita.Estado.PENDIENTE_VERIFICACION
        ),
    ).count()

    anticipos_verificados = (
        citas_base.filter(
            estado_pago=Cita.EstadoPago.VERIFICADO,
        ).aggregate(
            total=Sum("anticipo"),
        )["total"]
        or Decimal("0.00")
    )

    consulta = request.GET.get(
        "q",
        "",
    ).strip()

    estado = request.GET.get(
        "estado",
        "",
    ).strip()

    fecha_texto = request.GET.get(
        "fecha",
        "",
    ).strip()

    citas_filtradas = citas_base.all()

    if consulta:
        citas_filtradas = citas_filtradas.filter(
            Q(
                paciente__nombres__icontains=consulta,
            )
            | Q(
                paciente__apellidos__icontains=consulta,
            )
            | Q(
                paciente__cedula__icontains=consulta,
            )
            | Q(
                profesional__nombres__icontains=consulta,
            )
            | Q(
                profesional__apellidos__icontains=consulta,
            )
            | Q(
                servicio__nombre__icontains=consulta,
            )
            | Q(
                referencia_pago__icontains=consulta,
            )
        )

    estados_validos = {
        opcion[0]
        for opcion in Cita.Estado.choices
    }

    if estado in estados_validos:
        citas_filtradas = citas_filtradas.filter(
            estado=estado,
        )

    fecha_filtro = parse_date(
        fecha_texto
    )

    if fecha_filtro:
        citas_filtradas = citas_filtradas.filter(
            fecha=fecha_filtro,
        )

    citas_filtradas = citas_filtradas.order_by(
        "-creada_en",
    )

    paginador = Paginator(
        citas_filtradas,
        12,
    )

    pagina_citas = paginador.get_page(
        request.GET.get("pagina"),
    )

    contexto = {
        "nombre_usuario": nombre_usuario,
        "iniciales": iniciales or "U",
        "hoy": hoy,

        "total_usuarios": total_usuarios,
        "total_citas_hoy": total_citas_hoy,
        "pagos_pendientes": pagos_pendientes,
        "citas_confirmadas": citas_confirmadas,
        "citas_pendientes": citas_pendientes,

        "anticipos_verificados": (
            anticipos_verificados
        ),

        "citas_hoy": citas_hoy,
        "proximas_citas": proximas_citas,
        "pagina_citas": pagina_citas,

        "estados_cita": Cita.Estado.choices,

        "filtros": {
            "q": consulta,
            "estado": estado,
            "fecha": fecha_texto,
        },
    }

    return render(
        request,
        "core/panel.html",
        contexto,
    )


@staff_member_required(
    login_url="usuarios:login",
)
def detalle_cita(
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

    contexto = {
        "cita": cita,

        "puede_reprogramarse": (
            cita.estado
            not in {
                Cita.Estado.CANCELADA,
                Cita.Estado.COMPLETADA,
            }
        ),
    }

    return render(
        request,
        "core/detalle_cita.html",
        contexto,
    )


@staff_member_required(
    login_url="usuarios:login",
)
@transaction.atomic
def actualizar_cita(
    request,
    codigo,
):
    if request.method != "POST":
        return redirect(
            "core:detalle_cita",
            codigo=codigo,
        )

    cita = get_object_or_404(
        Cita.objects.select_for_update(),
        codigo=codigo,
    )

    accion = request.POST.get(
        "accion",
        "",
    )

    if accion == "verificar_pago":
        cita.estado_pago = (
            Cita.EstadoPago.VERIFICADO
        )

        if (
            cita.estado
            == Cita.Estado.PENDIENTE_VERIFICACION
        ):
            cita.estado = (
                Cita.Estado.CONFIRMADA
            )

        cita.save()

        messages.success(
            request,
            (
                "El pago fue verificado y la cita "
                "quedó confirmada."
            ),
        )

    elif accion == "rechazar_pago":
        cita.estado_pago = (
            Cita.EstadoPago.RECHAZADO
        )

        if cita.estado == Cita.Estado.CONFIRMADA:
            cita.estado = (
                Cita.Estado.PENDIENTE_VERIFICACION
            )

        cita.save()

        messages.warning(
            request,
            (
                "El pago fue marcado como rechazado."
            ),
        )

    elif accion == "confirmar_cita":
        if cita.estado in {
            Cita.Estado.CANCELADA,
            Cita.Estado.COMPLETADA,
        }:
            messages.error(
                request,
                (
                    "No se puede confirmar una cita "
                    "cancelada o completada."
                ),
            )

        else:
            cita.estado = Cita.Estado.CONFIRMADA
            cita.save()

            messages.success(
                request,
                "La cita fue confirmada.",
            )

    elif accion == "completar_cita":
        if cita.estado != Cita.Estado.CONFIRMADA:
            messages.error(
                request,
                (
                    "Primero debes confirmar la cita "
                    "antes de marcarla como completada."
                ),
            )

        else:
            cita.estado = Cita.Estado.COMPLETADA
            cita.save()

            messages.success(
                request,
                (
                    "La cita fue marcada "
                    "como completada."
                ),
            )

    elif accion == "cancelar_cita":
        if cita.estado == Cita.Estado.COMPLETADA:
            messages.error(
                request,
                (
                    "Una cita completada no puede "
                    "ser cancelada."
                ),
            )

        else:
            cita.estado = Cita.Estado.CANCELADA
            cita.save()

            messages.warning(
                request,
                "La cita fue cancelada.",
            )

    else:
        messages.error(
            request,
            (
                "La acción seleccionada "
                "no es válida."
            ),
        )

    return redirect(
        "core:detalle_cita",
        codigo=codigo,
    )


@staff_member_required(
    login_url="usuarios:login",
)
@transaction.atomic
def reprogramar_cita(
    request,
    codigo,
):
    cita = get_object_or_404(
        Cita.objects.select_for_update()
        .select_related(
            "paciente",
            "especialidad",
            "servicio",
            "profesional",
        ),
        codigo=codigo,
    )

    if cita.estado in {
        Cita.Estado.CANCELADA,
        Cita.Estado.COMPLETADA,
    }:
        messages.error(
            request,
            (
                "Una cita cancelada o completada "
                "no puede ser reprogramada."
            ),
        )

        return redirect(
            "core:detalle_cita",
            codigo=cita.codigo,
        )

    if request.method == "POST":
        fecha_texto = request.POST.get(
            "fecha",
            "",
        ).strip()

        hora_texto = request.POST.get(
            "hora",
            "",
        ).strip()

        fecha_nueva = parse_date(
            fecha_texto
        )

        hora_nueva = parsear_hora(
            hora_texto
        )

        if not fecha_nueva:
            messages.error(
                request,
                (
                    "Selecciona una fecha válida "
                    "para la cita."
                ),
            )

        elif fecha_nueva < timezone.localdate():
            messages.error(
                request,
                (
                    "La nueva fecha no puede "
                    "estar en el pasado."
                ),
            )

        elif not hora_nueva:
            messages.error(
                request,
                (
                    "Selecciona un horario válido "
                    "para la cita."
                ),
            )

        elif (
            fecha_nueva == cita.fecha
            and hora_nueva == cita.hora
        ):
            messages.info(
                request,
                (
                    "La cita mantiene la misma "
                    "fecha y hora."
                ),
            )

            return redirect(
                "core:detalle_cita",
                codigo=cita.codigo,
            )

        else:
            horas_disponibles = (
                obtener_horas_reprogramacion(
                    cita=cita,
                    fecha_seleccionada=(
                        fecha_nueva
                    ),
                )
            )

            hora_normalizada = (
                hora_nueva.strftime(
                    "%H:%M"
                )
            )

            if (
                hora_normalizada
                not in horas_disponibles
            ):
                messages.error(
                    request,
                    (
                        "El horario seleccionado ya no "
                        "se encuentra disponible."
                    ),
                )

            else:
                cita.fecha = fecha_nueva
                cita.hora = hora_nueva

                try:
                    cita.full_clean()
                    cita.save()

                except IntegrityError:
                    messages.error(
                        request,
                        (
                            "Ese horario acaba de ser "
                            "ocupado por otra cita."
                        ),
                    )

                else:
                    messages.success(
                        request,
                        (
                            "La cita fue reprogramada "
                            "correctamente."
                        ),
                    )

                    return redirect(
                        "core:detalle_cita",
                        codigo=cita.codigo,
                    )

    contexto = {
        "cita": cita,

        "fecha_actual": (
            cita.fecha.isoformat()
        ),

        "hora_actual": (
            cita.hora.strftime(
                "%H:%M"
            )
        ),
    }

    return render(
        request,
        "core/reprogramar_cita.html",
        contexto,
    )


@staff_member_required(
    login_url="usuarios:login",
)
@require_GET
def disponibilidad_reprogramacion(
    request,
    codigo,
):
    cita = get_object_or_404(
        Cita.objects.select_related(
            "profesional",
            "servicio",
        ),
        codigo=codigo,
    )

    anio_texto = request.GET.get(
        "anio",
        "",
    )

    mes_texto = request.GET.get(
        "mes",
        "",
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
                    "El año o el mes "
                    "no son válidos."
                )
            },
            status=400,
        )

    if mes < 1 or mes > 12:
        return JsonResponse(
            {
                "error": (
                    "El mes debe estar "
                    "entre 1 y 12."
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

        atiende_ese_dia = (
            HorarioProfesional.objects.filter(
                profesional=cita.profesional,
                dia_semana=(
                    fecha_actual.weekday()
                ),
                activo=True,
            ).exists()
        )

        if fecha_actual < hoy:
            estado = "pasada"

        elif not atiende_ese_dia:
            estado = "sin_atencion"

        else:
            horas = obtener_horas_reprogramacion(
                cita=cita,
                fecha_seleccionada=(
                    fecha_actual
                ),
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

                "es_fecha_actual": (
                    fecha_actual == cita.fecha
                ),
            }
        )

    return JsonResponse(
        {
            "mes": mes,
            "anio": anio,

            "primer_dia_semana": (
                fecha_inicio.weekday()
            ),

            "dias": dias,
        }
    )


@staff_member_required(
    login_url="usuarios:login",
)
@require_GET
def horarios_reprogramacion(
    request,
    codigo,
):
    cita = get_object_or_404(
        Cita.objects.select_related(
            "profesional",
            "servicio",
        ),
        codigo=codigo,
    )

    fecha_texto = request.GET.get(
        "fecha",
        "",
    )

    fecha_seleccionada = parse_date(
        fecha_texto
    )

    if not fecha_seleccionada:
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

    horas = obtener_horas_reprogramacion(
        cita=cita,
        fecha_seleccionada=(
            fecha_seleccionada
        ),
    )

    return JsonResponse(
        {
            "fecha": (
                fecha_seleccionada.isoformat()
            ),

            "horas": horas,

            "hora_actual": (
                cita.hora.strftime(
                    "%H:%M"
                )
                if fecha_seleccionada
                == cita.fecha
                else ""
            ),
        }
    )