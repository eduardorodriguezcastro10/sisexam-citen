from django.contrib import admin
from .models import AreaAcademica, Especialidad, Curso, Anio, Seccion, Pregunta, Opcion, ResultadoExamen, ExamenAsignado, UserProfile

admin.site.register(AreaAcademica)
admin.site.register(Especialidad)
admin.site.register(Curso)
admin.site.register(Anio)
admin.site.register(Seccion)
admin.site.register(Pregunta)
admin.site.register(Opcion)
admin.site.register(ResultadoExamen)
admin.site.register(ExamenAsignado)
admin.site.register(UserProfile)