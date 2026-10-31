from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    must_change_password = models.BooleanField(default=True)
    def __str__(self): return f"Perfil de {self.user.username}"

class AreaAcademica(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Especialidad(models.Model):
    area = models.ForeignKey(AreaAcademica, on_delete=models.CASCADE, related_name='especialidades')
    nombre = models.CharField(max_length=150, unique=True)
    siglas = models.CharField(max_length=10, blank=True)
    def __str__(self): return f"{self.nombre} ({self.siglas})"

class Curso(models.Model):
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='cursos')
    nombre = models.CharField(max_length=150)
    def __str__(self): return f"{self.nombre} - {self.especialidad.siglas}"

class Anio(models.Model):
    numero = models.IntegerField(choices=[(1,'Primer Año'),(2,'Segundo Año'),(3,'Tercer Año')], unique=True)
    def __str__(self): return f"{self.get_numero_display()}"

class Seccion(models.Model):
    letra = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')], unique=True)
    def __str__(self): return f"Sección {self.letra}"

class Pregunta(models.Model):
    TIPO_CHOICES = [
        ('OM', 'Opción Múltiple'), ('CORR', 'Correlación Simple'), ('CORR_CAUSA', 'Correlación Causa-Efecto'),
        ('CORR_DEF', 'Correlación Término-Definición'), ('VF', 'Verdadero/Falso'),
        ('COMP', 'Completar palabra'), ('LIBRE', 'Pregunta Libre'),
    ]
    NIVEL_CHOICES = [('FACIL', 'Fácil'), ('INTERMEDIO', 'Intermedio'), ('DIFICIL', 'Difícil')]
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='preguntas')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='FACIL')
    enunciado = models.TextField()
    contenido = models.JSONField(default=dict)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    anio = models.ForeignKey(Anio, on_delete=models.PROTECT)
    seccion = models.ForeignKey(Seccion, on_delete=models.PROTECT)
    origen_banco = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_ia = models.BooleanField(default=False)

    def __str__(self): return f"[{self.get_tipo_display()}] {self.enunciado[:50]}..."

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=300)
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)
    class Meta: ordering = ['orden']

class ExamenAsignado(models.Model):
    titulo = models.CharField(max_length=200)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE)
    tiempo_minutos = models.IntegerField(default=30)
    preguntas = models.ManyToManyField(Pregunta)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    def __str__(self): return f"{self.titulo} - {self.curso.nombre}"

class ResultadoExamen(models.Model):
    alumno = models.ForeignKey(User, on_delete=models.CASCADE, related_name='examenes_rendidos')
    examen_asignado = models.ForeignKey(ExamenAsignado, on_delete=models.SET_NULL, null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE)
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, null=True, blank=True)
    nota = models.FloatField(help_text="Nota vigesimal (0-20)")
    fecha_rendido = models.DateTimeField(auto_now_add=True)
    respuestas_detalle = models.JSONField(default=dict, blank=True)
    def __str__(self): return f"{self.alumno.username} - {self.curso.nombre} - Nota: {self.nota}"