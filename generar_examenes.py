import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citen_system.settings')
django.setup()

from core.models import Pregunta, Curso, Anio, Seccion, Opcion
from django.contrib.auth.models import User

docente = User.objects.first()
seccion = Seccion.objects.first() or Seccion.objects.create(letra='A')
anio = Anio.objects.first() or Anio.objects.create(numero=1)

print("Eliminando preguntas anteriores para empezar limpio...")
Pregunta.objects.all().delete()

cursos = Curso.objects.all()
print(f"Generando 20 preguntas variadas por cada curso ({len(cursos)} cursos)...")

for curso in cursos:
    # 1. Cinco de Opción Múltiple
    for i in range(1, 6):
        p_om = Pregunta.objects.create(
            curso=curso, tipo='OM', enunciado=f"OM Pregunta {i} de {curso.nombre}: ¿Cuál es el concepto clave?",
            contenido={}, creado_por=docente, anio=anio, seccion=seccion
        )
        Opcion.objects.create(pregunta=p_om, texto="Opción incorrecta A", es_correcta=False, orden=0)
        Opcion.objects.create(pregunta=p_om, texto=f"Respuesta correcta {i}", es_correcta=True, orden=1)
        Opcion.objects.create(pregunta=p_om, texto="Opción incorrecta B", es_correcta=False, orden=2)
        Opcion.objects.create(pregunta=p_om, texto="Opción incorrecta C", es_correcta=False, orden=3)

    # 2. Cinco de Verdadero/Falso
    for i in range(1, 6):
        Pregunta.objects.create(
            curso=curso, tipo='VF', enunciado=f"VF Pregunta {i} de {curso.nombre}: El estudio de esta materia es fundamental.",
            contenido={"correcta": i % 2 == 0}, # Alterna entre V y F
            creado_por=docente, anio=anio, seccion=seccion
        )

    # 3. Cinco de Completar
    for i in range(1, 6):
        Pregunta.objects.create(
            curso=curso, tipo='COMP', enunciado=f"COMP Pregunta {i} de {curso.nombre}: El concepto se denomina ________.",
            contenido={"palabra": f"Respuesta{i}"}, creado_por=docente, anio=anio, seccion=seccion
        )

    # 4. Cinco de Correlación
    for i in range(1, 6):
        Pregunta.objects.create(
            curso=curso, tipo='CORR', enunciado=f"CORR Pregunta {i} de {curso.nombre}: Relacione los conceptos.",
            contenido={"pares": {"Concepto A": "Definición A", "Concepto B": "Definición B", "Concepto C": "Definición C", "Concepto D": "Definición D"}},
            creado_por=docente, anio=anio, seccion=seccion
        )

print(f"¡ÉXITO! Se crearon 20 preguntas por curso. Total: {cursos.count() * 20} preguntas.")