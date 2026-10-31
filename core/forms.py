from django import forms
from .models import Pregunta, Curso, Anio, Seccion, Especialidad
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['curso', 'anio', 'seccion', 'tipo', 'enunciado']
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-control'}),
            'anio': forms.Select(attrs={'class': 'form-control'}),
            'seccion': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'id': 'select-tipo'}),
            'enunciado': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escriba aquí el enunciado completo de la pregunta...'}),
        }

class SubirArchivoForm(forms.Form):
    especialidad = forms.ModelChoiceField(queryset=Especialidad.objects.all(), label="Especialidad", widget=forms.Select(attrs={'class': 'form-control'}))
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), required=False, label="Curso Existente", widget=forms.Select(attrs={'class': 'form-control'}))
    nuevo_curso = forms.CharField(required=False, label="O Crear Nuevo Curso (Escriba el nombre)", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Programación Avanzada'}))
    anio = forms.ModelChoiceField(queryset=Anio.objects.all(), label="Año", widget=forms.Select(attrs={'class': 'form-control'}))
    seccion = forms.ModelChoiceField(queryset=Seccion.objects.all(), label="Sección", widget=forms.Select(attrs={'class': 'form-control'}))
    nombre_examen = forms.CharField(required=False, label="Título del Examen", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Examen Parcial 1'}))
    
    archivo = forms.FileField(label="Archivo (PDF, DOCX, PPTX)", widget=forms.FileInput(attrs={'class': 'form-control'}))
    cantidad = forms.IntegerField(min_value=1, max_value=30, initial=10, label="Cantidad de Preguntas", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20'}))
    porc_facil = forms.IntegerField(min_value=0, max_value=100, initial=40, label="Fácil (%)", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '40'}))
    porc_intermedio = forms.IntegerField(min_value=0, max_value=100, initial=40, label="Intermedio (%)", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '40'}))
    porc_dificil = forms.IntegerField(min_value=0, max_value=100, initial=20, label="Difícil (%)", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'}))
    
    incluir_om = forms.BooleanField(required=False, initial=True, label="Opción Múltiple", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    incluir_vf = forms.BooleanField(required=False, initial=True, label="Verdadero/Falso", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    incluir_comp = forms.BooleanField(required=False, initial=True, label="Completar palabra", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    incluir_corr = forms.BooleanField(required=False, initial=True, label="Correlación", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class UsuarioForm(UserCreationForm):
    ROL_CHOICES = (('Docentes', 'Docente'), ('Alumnos', 'Alumno'))
    rol = forms.ChoiceField(choices=ROL_CHOICES, label="Rol en el sistema", widget=forms.Select(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, required=True, label="Nombres", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, required=True, label="Apellidos", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class EditarUsuarioForm(forms.ModelForm):
    ROL_CHOICES = (('Administrador', 'Administrador'), ('Docentes', 'Docente'), ('Alumnos', 'Alumno'))
    rol = forms.ChoiceField(choices=ROL_CHOICES, label="Rol / Nivel de Acceso", widget=forms.Select(attrs={'class': 'form-control'}))
    activo = forms.BooleanField(required=False, label="Usuario Activo", widget=forms.CheckboxInput(attrs={'style': 'width: 20px; height: 20px; cursor: pointer;'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['activo'].initial = self.instance.is_active
            if self.instance.is_superuser: self.fields['rol'].initial = 'Administrador'
            elif self.instance.groups.filter(name='Docentes').exists(): self.fields['rol'].initial = 'Docentes'
            else: self.fields['rol'].initial = 'Alumnos'

class CambiarPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'