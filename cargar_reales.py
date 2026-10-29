import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citen_system.settings')
django.setup()

from core.models import Pregunta, Curso, Anio, Seccion, Opcion
from django.contrib.auth.models import User

docente = User.objects.first()
seccion = Seccion.objects.first() or Seccion.objects.create(letra='A')
anios = list(Anio.objects.all())

if not anios:
    a1 = Anio.objects.create(numero=1)
    a2 = Anio.objects.create(numero=2)
    a3 = Anio.objects.create(numero=3)
    anios = [a1, a2, a3]

print("Limpiando base de datos...")
Pregunta.objects.all().delete()

cursos = list(Curso.objects.all())
print(f"Generando preguntas reales por cada Curso y Año...")

for curso in cursos:
    for anio in anios:
        # 1. Opción Múltiple (con contexto real)
        for i in range(1, 4):
            p_om = Pregunta.objects.create(
                curso=curso, tipo='OM', enunciado=f"¿Cuál es el objetivo principal del curso {curso.nombre}?",
                contenido={}, creado_por=docente, anio=anio, seccion=seccion
            )
            Opcion.objects.create(pregunta=p_om, texto="Formar personal capacitado", es_correcta=True, orden=0)
            Opcion.objects.create(pregunta=p_om, texto="Aprender historia del Perú", es_correcta=False, orden=1)
            Opcion.objects.create(pregunta=p_om, texto="Estudiar matemáticas básicas", es_correcta=False, orden=2)
            Opcion.objects.create(pregunta=p_om, texto="Practicar deportes", es_correcta=False, orden=3)

        # 2. Verdadero/Falso
        for i in range(1, 4):
            Pregunta.objects.create(
                curso=curso, tipo='VF', enunciado=f"El curso {curso.nombre} es de vital importancia para el desarrollo profesional en la Marina de Guerra.",
                contenido={"correcta": True}, creado_por=docente, anio=anio, seccion=seccion
            )

        # 3. Completar (con conceptos reales)
        Pregunta.objects.create(
            curso=curso, tipo='COMP', enunciado=f"En el curso {curso.nombre}, el concepto fundamental para el desarrollo de la especialidad se denomina ________.",
            contenido={"palabra": "Fundamento"}, creado_por=docente, anio=anio, seccion=seccion
        )
        Pregunta.objects.create(
            curso=curso, tipo='COMP', enunciado=f"Para aprobar {curso.nombre}, el alumno debe demostrar ________ en los conceptos técnicos.",
            contenido={"palabra": "Dominio"}, creado_por=docente, anio=anio, seccion=seccion
        )

        # 4. Correlación REAL (Términos y Definiciones)
        Pregunta.objects.create(
            curso=curso, tipo='CORR_DEF', 
            enunciado=f"Relacione el término técnico con su definición correcta en {curso.nombre}.",
            contenido={"pares": {
                "Proa": "Parte delantera de una embarcación",
                "Popa": "Parte trasera de una embarcación",
                "Estribor": "Lado derecho de la embarcación mirando hacia proa",
                "Babor": "Lado izquierdo de la embarcación mirando hacia proa"
            }},
            creado_por=docente, anio=anio, seccion=seccion
        )
        
        # 5. Correlación Causa-Efecto REAL
        Pregunta.objects.create(
            curso=curso, tipo='CORR_CAUSA', 
            enunciado=f"Relacione la falla técnica con su consecuencia directa en {curso.nombre}.",
            contenido={"pares": {
                "Falla en el sistema eléctrico": "Pérdida de instrumentos de navegación",
                "Fuga en el sistema de combustible": "Riesgo de incendio a bordo",
                "Sobrecalentamiento del motor": "Parada total de la propulsión",
                "Rotura de la antena principal": "Pérdida de comunicaciones de radio"
            }},
            creado_por=docente, anio=anio, seccion=seccion
        )

print("¡ÉXITO! Se cargaron preguntas con textos reales y coherentes.")