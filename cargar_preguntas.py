import os
import django

# Configurar el entorno de Django para que el script funcione
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citen_system.settings')
django.setup()

from core.models import Pregunta, Curso, Anio, Seccion, Opcion
from django.contrib.auth.models import User

docente = User.objects.first()
seccion = Seccion.objects.first()

if not seccion:
    seccion = Seccion.objects.create(letra='A')

anio = Anio.objects.first()
if not anio:
    anio = Anio.objects.create(numero=1)

cursos = list(Curso.objects.all())
print(f"Se encontraron {len(cursos)} cursos en la base de datos.")

for curso in cursos:
    cant_previas = Pregunta.objects.filter(curso=curso).count()
    print(f"-> Curso: {curso.nombre} | Preguntas actuales: {cant_previas}")
    
    # Si el curso tiene menos de 6 preguntas, le inyectamos los 4 tipos
    if cant_previas < 6:
        # 1. Opción Múltiple
        p_om = Pregunta.objects.create(
            curso=curso, tipo='OM', enunciado=f"¿Cuál es un tema clave de {curso.nombre}?",
            contenido={}, creado_por=docente, anio=anio, seccion=seccion
        )
        Opcion.objects.create(pregunta=p_om, texto="Historia Universal", es_correcta=False, orden=0)
        Opcion.objects.create(pregunta=p_om, texto=f"Conceptos de {curso.nombre}", es_correcta=True, orden=1)
        Opcion.objects.create(pregunta=p_om, texto="Matemática Básica", es_correcta=False, orden=2)
        Opcion.objects.create(pregunta=p_om, texto="Educación Física", es_correcta=False, orden=3)

        # 2. Verdadero/Falso
        Pregunta.objects.create(
            curso=curso, tipo='VF', enunciado=f"El estudio de {curso.nombre} es fundamental.",
            contenido={"correcta": True}, creado_por=docente, anio=anio, seccion=seccion
        )

        # 3. Completar Palabra
        Pregunta.objects.create(
            curso=curso, tipo='COMP', enunciado=f"El concepto más importante de {curso.nombre} se denomina ________.",
            contenido={"palabra": "Fundamento"}, creado_por=docente, anio=anio, seccion=seccion
        )

        # 4. Correlación Simple
        Pregunta.objects.create(
            curso=curso, tipo='CORR', enunciado=f"Relacione los conceptos de {curso.nombre}.",
            contenido={"pares": {"Fragata": "Guerra ASW", "Remolcador": "Apoyo logístico", "Submarino": "Ataque silencioso", "Portaviones": "Proyección aérea"}},
            creado_por=docente, anio=anio, seccion=seccion
        )
        
        # 5. Correlación Causa-Efecto
        Pregunta.objects.create(
            curso=curso, tipo='CORR_CAUSA', enunciado=f"Relacione causa y efecto en {curso.nombre}.",
            contenido={"pares": {"Falla generador": "Pérdida de navegación", "Sobrecalentamiento": "Parada de motor", "Fuga hidráulica": "Bloqueo de timón", "Rotura de antena": "Pérdida de radio"}},
            creado_por=docente, anio=anio, seccion=seccion
        )

        # 6. Correlación Término-Definición
        Pregunta.objects.create(
            curso=curso, tipo='CORR_DEF', enunciado=f"Relacione el término con su definición en {curso.nombre}.",
            contenido={"pares": {"Estribor": "Lado derecho", "Babor": "Lado izquierdo", "Proa": "Parte delantera", "Popa": "Parte trasera"}},
            creado_por=docente, anio=anio, seccion=seccion
        )
        print(f"   [OK] Se agregaron 6 preguntas a {curso.nombre}.")
    else:
        print(f"   [INFO] {curso.nombre} ya tiene suficientes preguntas.")

print("¡Proceso terminado con éxito!")