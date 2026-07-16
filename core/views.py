from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def inicio(request):
    return render(
        request,
        "core/inicio.html",
    )


@login_required
def panel(request):
    nombre_completo = request.user.get_full_name().strip()

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

    contexto = {
        "nombre_usuario": nombre_usuario,
        "iniciales": iniciales or "U",

        "total_clientes": 248,
        "clientes_activos": 183,
        "citas_agendadas": 36,
        "nuevos_clientes": 18,

        "proximas_citas": [
            {
                "hora": "09:00",
                "cliente": "María Zambrano",
                "servicio": "Tratamiento facial",
                "profesional": "Camila González",
                "estado": "Confirmada",
                "clase_estado": "confirmada",
            },
            {
                "hora": "10:30",
                "cliente": "Carlos Mendoza",
                "servicio": "Corte de cabello",
                "profesional": "José Andrade",
                "estado": "Pendiente",
                "clase_estado": "pendiente",
            },
            {
                "hora": "12:00",
                "cliente": "Ana López",
                "servicio": "Manicure",
                "profesional": "Sofía Vera",
                "estado": "Confirmada",
                "clase_estado": "confirmada",
            },
            {
                "hora": "15:30",
                "cliente": "Luis Cedeño",
                "servicio": "Masaje relajante",
                "profesional": "Daniela Mera",
                "estado": "Pendiente",
                "clase_estado": "pendiente",
            },
        ],
    }

    return render(
        request,
        "core/panel.html",
        contexto,
    )