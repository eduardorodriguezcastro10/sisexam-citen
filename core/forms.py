from django import forms
from .models import Pregunta, Curso, Anio

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['curso', 'anio', 'seccion', 'tipo', 'enunciado']
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'anio': forms.Select(attrs={'class': 'form-select'}),
            'seccion': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'select-tipo'}),
            'enunciado': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escriba aquí el enunciado completo de la pregunta...'}),
        }

class SubirArchivoForm(forms.Form):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(), 
        label="Curso Destino", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    anio = forms.ModelChoiceField(
        queryset=Anio.objects.all(), 
        label="Año Destino", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    archivo = forms.FileField(
        label="Seleccione un archivo (PDF, DOCX, PPTX)",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )