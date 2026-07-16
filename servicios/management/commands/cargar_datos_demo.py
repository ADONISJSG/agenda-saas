from decimal import Decimal

from django.core.management.base import BaseCommand

from servicios.models import (
    Especialidad,
    Profesional,
    Servicio,
)


class Command(BaseCommand):
    help = (
        "Carga especialidades, profesionales "
        "y servicios de demostración."
    )

    def handle(self, *args, **options):
        psicologia, _ = Especialidad.objects.update_or_create(
            nombre="Psicología",
            defaults={
                "descripcion": (
                    "Atención psicológica y "
                    "acompañamiento emocional."
                ),
                "activa": True,
            },
        )

        odontologia, _ = Especialidad.objects.update_or_create(
            nombre="Odontología",
            defaults={
                "descripcion": (
                    "Evaluación y tratamientos "
                    "para la salud bucal."
                ),
                "activa": True,
            },
        )

        fisioterapia, _ = Especialidad.objects.update_or_create(
            nombre="Fisioterapia",
            defaults={
                "descripcion": (
                    "Rehabilitación física y "
                    "recuperación funcional."
                ),
                "activa": True,
            },
        )

        medicina_general, _ = Especialidad.objects.update_or_create(
            nombre="Medicina general",
            defaults={
                "descripcion": (
                    "Consulta médica general, "
                    "evaluación y diagnóstico."
                ),
                "activa": True,
            },
        )

        servicios = [
            {
                "especialidad": psicologia,
                "nombre": "Consulta psicológica",
                "descripcion": (
                    "Consulta individual con profesional "
                    "de psicología."
                ),
                "duracion": 60,
                "precio": Decimal("35.00"),
            },
            {
                "especialidad": psicologia,
                "nombre": "Terapia de pareja",
                "descripcion": (
                    "Sesión de acompañamiento "
                    "para parejas."
                ),
                "duracion": 75,
                "precio": Decimal("50.00"),
            },
            {
                "especialidad": odontologia,
                "nombre": "Evaluación odontológica",
                "descripcion": (
                    "Revisión general del estado "
                    "de la salud bucal."
                ),
                "duracion": 45,
                "precio": Decimal("25.00"),
            },
            {
                "especialidad": odontologia,
                "nombre": "Limpieza dental",
                "descripcion": (
                    "Limpieza profesional y "
                    "eliminación de placa."
                ),
                "duracion": 60,
                "precio": Decimal("40.00"),
            },
            {
                "especialidad": fisioterapia,
                "nombre": "Sesión de fisioterapia",
                "descripcion": (
                    "Evaluación y tratamiento "
                    "de recuperación física."
                ),
                "duracion": 60,
                "precio": Decimal("30.00"),
            },
            {
                "especialidad": fisioterapia,
                "nombre": "Masaje terapéutico",
                "descripcion": (
                    "Masaje profesional para "
                    "dolor y tensión muscular."
                ),
                "duracion": 45,
                "precio": Decimal("28.00"),
            },
            {
                "especialidad": medicina_general,
                "nombre": "Consulta médica general",
                "descripcion": (
                    "Consulta, evaluación y "
                    "orientación médica."
                ),
                "duracion": 40,
                "precio": Decimal("30.00"),
            },
            {
                "especialidad": medicina_general,
                "nombre": "Control médico",
                "descripcion": (
                    "Seguimiento de diagnóstico "
                    "o tratamiento anterior."
                ),
                "duracion": 30,
                "precio": Decimal("20.00"),
            },
        ]

        for datos in servicios:
            Servicio.objects.update_or_create(
                especialidad=datos["especialidad"],
                nombre=datos["nombre"],
                defaults={
                    "descripcion": datos["descripcion"],
                    "duracion_minutos": datos["duracion"],
                    "precio": datos["precio"],
                    "activo": True,
                },
            )

        profesionales = [
            {
                "especialidad": psicologia,
                "nombres": "Andrea",
                "apellidos": "López",
                "telefono": "0991111111",
                "correo": "andrea@example.com",
            },
            {
                "especialidad": psicologia,
                "nombres": "Carlos",
                "apellidos": "Mendoza",
                "telefono": "0992222222",
                "correo": "carlos@example.com",
            },
            {
                "especialidad": odontologia,
                "nombres": "María",
                "apellidos": "Zambrano",
                "telefono": "0993333333",
                "correo": "maria@example.com",
            },
            {
                "especialidad": odontologia,
                "nombres": "José",
                "apellidos": "Andrade",
                "telefono": "0994444444",
                "correo": "jose@example.com",
            },
            {
                "especialidad": fisioterapia,
                "nombres": "Daniela",
                "apellidos": "Mera",
                "telefono": "0995555555",
                "correo": "daniela@example.com",
            },
            {
                "especialidad": fisioterapia,
                "nombres": "Luis",
                "apellidos": "Cedeño",
                "telefono": "0996666666",
                "correo": "luis@example.com",
            },
            {
                "especialidad": medicina_general,
                "nombres": "Sofía",
                "apellidos": "Vera",
                "telefono": "0997777777",
                "correo": "sofia@example.com",
            },
            {
                "especialidad": medicina_general,
                "nombres": "Miguel",
                "apellidos": "Moreira",
                "telefono": "0998888888",
                "correo": "miguel@example.com",
            },
        ]

        for datos in profesionales:
            Profesional.objects.update_or_create(
                especialidad=datos["especialidad"],
                nombres=datos["nombres"],
                apellidos=datos["apellidos"],
                defaults={
                    "telefono": datos["telefono"],
                    "correo": datos["correo"],
                    "activo": True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Especialidades, servicios y "
                "profesionales cargados correctamente."
            )
        )