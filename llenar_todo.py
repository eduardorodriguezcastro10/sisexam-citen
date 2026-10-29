import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citen_system.settings')
django.setup()

from core.models import Pregunta, Curso, Anio, Seccion, Opcion
from django.contrib.auth.models import User

docente = User.objects.first()
seccion = Seccion.objects.first() or Seccion.objects.create(letra='A')

# Aseguramos que existan los 3 años
anios = list(Anio.objects.all())
if not anios:
    a1 = Anio.objects.create(numero=1)
    a2 = Anio.objects.create(numero=2)
    a3 = Anio.objects.create(numero=3)
    anios = [a1, a2, a3]

print("Limpiando base de datos...")
Pregunta.objects.all().delete()

cursos = list(Curso.objects.all())
print(f"Generando 20 preguntas por cada combinación de Curso y Año ({len(cursos)} cursos x {len(anios)} años)...")

total = 0
for curso in cursos:
    for anio in anios:
        # 1. Cinco de Opción Múltiple
        for i in range(1, 6):
            p_om = Pregunta.objects.create(
                curso=curso, tipo='OM', enunciado=f"OM {i} ({curso.nombre} - {anio}): ¿Cuál es el concepto clave?",
                contenido={}, creado_por=docente, anio=anio, seccion=seccion
            )
            Opcion.objects.create(pregunta=p_om, texto="Incorrecta A", es_correcta=False, orden=0)
            Opcion.objects.create(pregunta=p_om, texto=f"Correcta {i}", es_correcta=True, orden=1)
            Opcion.objects.create(pregunta=p_om, texto="Incorrecta B", es_correcta=False, orden=2)
            Opcion.objects.create(pregunta=p_om, texto="Incorrecta C", es_correcta=False, orden=3)

        # 2. Cinco de Verdadero/Falso
        for i in range(1, 6):
            Pregunta.objects.create(
                curso=curso, tipo='VF', enunciado=f"VF {i} ({curso.nombre} - {anio}): El estudio es fundamental.",
                contenido={"correcta": i % 2 == 0}, creado_por=docente, anio=anio, seccion=seccion
            )

        # 3. Cinco de Completar
        for i in range(1, 6):
            Pregunta.objects.create(
                curso=curso, tipo='COMP', enunciado=f"COMP {i} ({curso.nombre} - {anio}): El concepto se denomina ________.",
                contenido={"palabra": f"Respuesta{i}"}, creado_por=docente, anio=anio, seccion=seccion
            )

        # 4. Cinco de Correlación
        for i in range(1, 6):
            Pregunta.objects.create(
                curso=curso, tipo='CORR', enunciado=f"CORR {i} ({curso.nombre} - {anio}): Relacione los conceptos.",
                contenido={"pares": {"Concepto A": "Definición A", "Concepto B": "Definición B", "Concepto C": "Definición C", "Concepto D": "Definición D"}},
                creado_por=docente, anio=anio, seccion=seccion
            )
        total += 20

print(f"¡ÉXITO TOTAL! Se crearon {total} preguntas en la base de datos.")