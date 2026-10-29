import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citen_system.settings')
django.setup()

from django.contrib.auth.models import User, Group

# 1. Crear los grupos si no existen
grupo_docentes, _ = Group.objects.get_or_create(name='Docentes')
grupo_alumnos, _ = Group.objects.get_or_create(name='Alumnos')

# 2. Crear usuario Docente
docente, creado_d = User.objects.get_or_create(username='docente_prueba')
docente.set_password('Citen2024*')
docente.is_staff = True # Para que pueda entrar al admin
docente.save()
docente.groups.add(grupo_docentes)

# 3. Crear usuario Alumno
alumno, creado_a = User.objects.get_or_create(username='alumno_prueba')
alumno.set_password('Citen2024*')
alumno.save()
alumno.groups.add(grupo_alumnos)

print("¡Usuarios creados con éxito!")
print("Docente: docente_prueba / Citen2024*")
print("Alumno:  alumno_prueba / Citen2024*")