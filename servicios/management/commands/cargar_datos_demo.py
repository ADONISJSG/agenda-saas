from datetime import time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Opinion
from servicios.models import (
    Especialidad,
    HorarioProfesional,
    Profesional,
    Servicio,
)


class Command(BaseCommand):
    help = (
        "Crea categorías, servicios, profesionales, "
        "horarios y opiniones de demostración."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        especialidades = [
            {
                "nombre": "Barbería",
                "descripcion": (
                    "Servicios de corte, arreglo de barba "
                    "y cuidado personal."
                ),
                "servicios": [
                    {
                        "nombre": "Corte clásico",
                        "duracion": 45,
                        "precio": "12.00",
                    },
                    {
                        "nombre": "Corte y barba",
                        "duracion": 60,
                        "precio": "18.00",
                    },
                ],
                "profesionales": [
                    {
                        "nombres": "Carlos",
                        "apellidos": "Mendoza",
                        "telefono": "0991111111",
                        "correo": "carlos@example.com",
                    },
                    {
                        "nombres": "Luis",
                        "apellidos": "Zambrano",
                        "telefono": "0992222222",
                        "correo": "luis@example.com",
                    },
                ],
            },
            {
                "nombre": "Belleza y estética",
                "descripcion": (
                    "Atención para cuidado facial, uñas, "
                    "maquillaje y tratamientos estéticos."
                ),
                "servicios": [
                    {
                        "nombre": "Manicura completa",
                        "duracion": 60,
                        "precio": "15.00",
                    },
                    {
                        "nombre": "Limpieza facial",
                        "duracion": 75,
                        "precio": "25.00",
                    },
                ],
                "profesionales": [
                    {
                        "nombres": "María",
                        "apellidos": "López",
                        "telefono": "0993333333",
                        "correo": "maria@example.com",
                    },
                    {
                        "nombres": "Andrea",
                        "apellidos": "Cedeño",
                        "telefono": "0994444444",
                        "correo": "andrea@example.com",
                    },
                ],
            },
            {
                "nombre": "Consultoría",
                "descripcion": (
                    "Asesorías y consultas profesionales "
                    "personalizadas."
                ),
                "servicios": [
                    {
                        "nombre": "Consulta inicial",
                        "duracion": 60,
                        "precio": "30.00",
                    },
                    {
                        "nombre": "Asesoría especializada",
                        "duracion": 90,
                        "precio": "45.00",
                    },
                ],
                "profesionales": [
                    {
                        "nombres": "José",
                        "apellidos": "Vera",
                        "telefono": "0995555555",
                        "correo": "jose@example.com",
                    },
                    {
                        "nombres": "Daniela",
                        "apellidos": "Moreira",
                        "telefono": "0996666666",
                        "correo": "daniela@example.com",
                    },
                ],
            },
            {
                "nombre": "Entrenamiento personal",
                "descripcion": (
                    "Sesiones individuales de entrenamiento "
                    "y acompañamiento físico."
                ),
                "servicios": [
                    {
                        "nombre": "Evaluación inicial",
                        "duracion": 45,
                        "precio": "20.00",
                    },
                    {
                        "nombre": "Sesión personalizada",
                        "duracion": 60,
                        "precio": "25.00",
                    },
                ],
                "profesionales": [
                    {
                        "nombres": "Miguel",
                        "apellidos": "Alcívar",
                        "telefono": "0997777777",
                        "correo": "miguel@example.com",
                    },
                    {
                        "nombres": "Sofía",
                        "apellidos": "Mero",
                        "telefono": "0998888888",
                        "correo": "sofia@example.com",
                    },
                ],
            },
        ]

        total_especialidades = 0
        total_servicios = 0
        total_profesionales = 0
        total_horarios = 0

        for datos_especialidad in especialidades:
            especialidad, creada = (
                Especialidad.objects.update_or_create(
                    nombre=datos_especialidad["nombre"],
                    defaults={
                        "descripcion": (
                            datos_especialidad["descripcion"]
                        ),
                        "activa": True,
                    },
                )
            )

            if creada:
                total_especialidades += 1

            for datos_servicio in datos_especialidad[
                "servicios"
            ]:
                _, servicio_creado = (
                    Servicio.objects.update_or_create(
                        especialidad=especialidad,
                        nombre=datos_servicio["nombre"],
                        defaults={
                            "descripcion": "",
                            "duracion_minutos": (
                                datos_servicio["duracion"]
                            ),
                            "precio": Decimal(
                                datos_servicio["precio"]
                            ),
                            "activo": True,
                        },
                    )
                )

                if servicio_creado:
                    total_servicios += 1

            for datos_profesional in datos_especialidad[
                "profesionales"
            ]:
                profesional, profesional_creado = (
                    Profesional.objects.update_or_create(
                        especialidad=especialidad,
                        nombres=datos_profesional["nombres"],
                        apellidos=datos_profesional["apellidos"],
                        defaults={
                            "telefono": (
                                datos_profesional["telefono"]
                            ),
                            "correo": (
                                datos_profesional["correo"]
                            ),
                            "activo": True,
                        },
                    )
                )

                if profesional_creado:
                    total_profesionales += 1

                total_horarios += self.crear_horarios(
                    profesional
                )

        self.crear_opiniones()

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de demostración cargados correctamente."
            )
        )

        self.stdout.write(
            f"Especialidades nuevas: {total_especialidades}"
        )

        self.stdout.write(
            f"Servicios nuevos: {total_servicios}"
        )

        self.stdout.write(
            f"Profesionales nuevos: {total_profesionales}"
        )

        self.stdout.write(
            f"Horarios nuevos: {total_horarios}"
        )

    def crear_horarios(self, profesional):
        creados = 0

        # Lunes a viernes: jornada de mañana
        for dia in range(0, 5):
            _, creado = (
                HorarioProfesional.objects.get_or_create(
                    profesional=profesional,
                    dia_semana=dia,
                    hora_inicio=time(8, 0),
                    hora_fin=time(12, 0),
                    defaults={
                        "intervalo_minutos": 30,
                        "activo": True,
                    },
                )
            )

            if creado:
                creados += 1

        # Lunes a viernes: jornada de tarde
        for dia in range(0, 5):
            _, creado = (
                HorarioProfesional.objects.get_or_create(
                    profesional=profesional,
                    dia_semana=dia,
                    hora_inicio=time(14, 0),
                    hora_fin=time(18, 0),
                    defaults={
                        "intervalo_minutos": 30,
                        "activo": True,
                    },
                )
            )

            if creado:
                creados += 1

        # Sábado
        _, creado = HorarioProfesional.objects.get_or_create(
            profesional=profesional,
            dia_semana=5,
            hora_inicio=time(9, 0),
            hora_fin=time(13, 0),
            defaults={
                "intervalo_minutos": 30,
                "activo": True,
            },
        )

        if creado:
            creados += 1

        return creados

    def crear_opiniones(self):
        opiniones = [
            {
                "nombre": "María López",
                "calificacion": 5,
                "comentario": (
                    "El proceso fue rápido y pude escoger "
                    "el horario que más me convenía."
                ),
                "destacada": True,
            },
            {
                "nombre": "Luis Carrillo",
                "calificacion": 5,
                "comentario": (
                    "La plataforma es fácil de utilizar "
                    "y muestra claramente la disponibilidad."
                ),
                "destacada": True,
            },
            {
                "nombre": "Daniela Zambrano",
                "calificacion": 4,
                "comentario": (
                    "Encontré al profesional que necesitaba "
                    "y pude agendar sin complicaciones."
                ),
                "destacada": False,
            },
        ]

        for datos in opiniones:
            Opinion.objects.update_or_create(
                nombre=datos["nombre"],
                comentario=datos["comentario"],
                defaults={
                    "calificacion": datos["calificacion"],
                    "aprobada": True,
                    "destacada": datos["destacada"],
                },
            )