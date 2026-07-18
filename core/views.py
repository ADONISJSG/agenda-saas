from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import (
    staff_member_required,
)
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.utils.dateparse import parse_date

from reservas.models import Cita
from usuarios.models import Paciente


def inicio(request):
    return render(
        request,
        "core/inicio.html",
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

    pagos_pendientes = citas_base.filter(
        estado_pago=Cita.EstadoPago.PENDIENTE,
    ).exclude(
        estado=Cita.Estado.CANCELADA,
    ).count()

    citas_confirmadas = citas_base.filter(
        estado=Cita.Estado.CONFIRMADA,
    ).count()

    citas_pendientes = citas_base.filter(
        estado=Cita.Estado.PENDIENTE_VERIFICACION,
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

    fecha_filtro = parse_date(fecha_texto)

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
                    "La cita fue marcada como completada."
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
            "La acción seleccionada no es válida.",
        )

    return redirect(
        "core:detalle_cita",
        codigo=codigo,
    )