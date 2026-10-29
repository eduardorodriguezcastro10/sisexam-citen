import json
import random
import os
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse

from pypdf import PdfReader
import docx
from pptx import Presentation
from openai import OpenAI

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from .forms import PreguntaForm, SubirArchivoForm
from .models import Pregunta, Opcion, Especialidad, Curso, Anio, Seccion, ResultadoExamen

def docente_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Docentes').exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Acceso denegado. Esta sección es exclusiva para Docentes.")
            return redirect('home')
    return _wrapped_view

@login_required
def home(request):
    es_docente = request.user.is_superuser or request.user.groups.filter(name='Docentes').exists()
    especialidades = Especialidad.objects.all()
    cursos = Curso.objects.all()
    anios = Anio.objects.all()
    return render(request, 'core/home.html', {'es_docente': es_docente, 'especialidades': especialidades, 'cursos': cursos, 'anios': anios})

@login_required
@docente_required
def registrar_pregunta(request):
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.creado_por = request.user
            tipo = form.cleaned_data['tipo']
            if tipo in ['CORR', 'CORR_CAUSA', 'CORR_DEF']:
                pares = {}
                for i in range(1, 6):
                    a = request.POST.get(f'corr_a_{i}', '')
                    b = request.POST.get(f'corr_b_{i}', '')
                    if a and b: pares[a] = b
                pregunta.contenido = {"pares": pares}
            elif tipo == 'VF':
                pregunta.contenido = {"correcta": request.POST.get('vf_respuesta') == 'true'}
            elif tipo == 'COMP':
                pregunta.contenido = {"palabra": request.POST.get('comp_palabra', '')}
            pregunta.save()
            if tipo == 'OM':
                opciones = [request.POST.get('om_a', ''), request.POST.get('om_b', ''), request.POST.get('om_c', ''), request.POST.get('om_d', '')]
                correcta_idx = int(request.POST.get('om_correcta', 0))
                for idx, texto in enumerate(opciones):
                    if texto: Opcion.objects.create(pregunta=pregunta, texto=texto, es_correcta=(idx == correcta_idx), orden=idx)
            messages.success(request, "Pregunta registrada exitosamente.")
            return redirect('home')
    else:
        form = PreguntaForm()
    return render(request, 'core/registrar_pregunta.html', {'form': form})

def extraer_texto(archivo):
    texto = ""
    nombre = archivo.name.lower()
    try:
        if nombre.endswith('.pdf'):
            reader = PdfReader(archivo)
            for page in reader.pages: texto += (page.extract_text() or "") + "\n"
        elif nombre.endswith('.docx'):
            doc = docx.Document(archivo)
            for para in doc.paragraphs: texto += para.text + "\n"
        elif nombre.endswith('.pptx'):
            prs = Presentation(archivo)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"): texto += shape.text + "\n"
        else:
            raise ValueError("Formato no soportado.")
    except Exception as e:
        raise ValueError(f"Error al leer el archivo: {str(e)}")
    return texto

@login_required
@docente_required
def subir_material(request):
    if request.method == 'POST':
        form = SubirArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                texto = extraer_texto(archivo)
                if not texto.strip(): return render(request, 'core/subir_material.html', {'form': form, 'error': "El archivo no tiene texto legible."})
                
                texto_recortado = texto[:4000]
                api_key = os.getenv('GROQ_API_KEY')
                if not api_key: return render(request, 'core/subir_material.html', {'form': form, 'error': "Falta configurar la API KEY en .env"})
                
                client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                respuesta = client.chat.completions.create(
                    model="openai/gpt-oss-20b", response_format={ "type": "json_object" }, 
                    messages=[
                        {"role": "system", "content": "Eres un profesor experto. A partir del texto, genera exactamente 5 preguntas de opción múltiple. Devuelve un JSON estricto con esta estructura: {\"preguntas\": [{\"enunciado\": \"...\", \"opciones\": [\"A\", \"B\", \"C\", \"D\"], \"correcta\": 0}]}"},
                        {"role": "user", "content": texto_recortado}
                    ]
                )
                
                datos_ia = json.loads(respuesta.choices[0].message.content)
                preguntas_creadas = 0
                curso_seleccionado = form.cleaned_data['curso']
                anio_seleccionado = form.cleaned_data['anio']
                seccion_default = Seccion.objects.first()
                
                for item in datos_ia.get('preguntas', []):
                    p = Pregunta.objects.create(
                        curso=curso_seleccionado, tipo='OM', enunciado=item.get('enunciado', 'Pregunta sin título'), 
                        contenido={}, creado_por=request.user, anio=anio_seleccionado, seccion=seccion_default, es_ia=True 
                    )
                    for idx, opt_texto in enumerate(item.get('opciones', [])):
                        Opcion.objects.create(pregunta=p, texto=opt_texto, es_correcta=(idx == item.get('correcta', 0)), orden=idx)
                    preguntas_creadas += 1
                    
                return render(request, 'core/subir_material.html', {'form': SubirArchivoForm(), 'mensaje_exito': f"¡Éxito! Se generaron {preguntas_creadas} preguntas con IA para {curso_seleccionado.nombre}."})
            except Exception as e:
                return render(request, 'core/subir_material.html', {'form': form, 'error': f"Error: {str(e)}"})
    else:
        form = SubirArchivoForm()
    return render(request, 'core/subir_material.html', {'form': form})

@login_required
@docente_required
def ver_reportes(request):
    query = request.GET.get('q', '')
    origen = request.GET.get('origen', '') 
    
    preguntas_list = Pregunta.objects.all()
    if query: preguntas_list = preguntas_list.filter(enunciado__icontains=query)
    if origen == 'manual': preguntas_list = preguntas_list.filter(es_ia=False)
    elif origen == 'ia': preguntas_list = preguntas_list.filter(es_ia=True)
        
    preguntas_list = preguntas_list.order_by('-fecha_creacion')
    
    paginator = Paginator(preguntas_list, 10) 
    preguntas = paginator.get_page(request.GET.get('page'))

    tipos_data = {'labels': ['Opción Múltiple', 'Correlaciones', 'Verdadero/Falso', 'Completar'], 'values': [Pregunta.objects.filter(tipo='OM').count(), Pregunta.objects.filter(tipo__startswith='CORR').count(), Pregunta.objects.filter(tipo='VF').count(), Pregunta.objects.filter(tipo='COMP').count()]}
    from django.db.models import Avg
    notas_por_curso = ResultadoExamen.objects.values('curso__nombre').annotate(promedio=Avg('nota')).order_by('-promedio')[:5]
    notas_data = {'labels': [item['curso__nombre'] for item in notas_por_curso], 'values': [round(item['promedio'], 2) for item in notas_por_curso]}
    
    context = {
        'total': Pregunta.objects.count(), 'count_om': Pregunta.objects.filter(tipo='OM').count(), 'count_corr': Pregunta.objects.filter(tipo__startswith='CORR').count(), 'count_vf': Pregunta.objects.filter(tipo='VF').count(), 'count_comp': Pregunta.objects.filter(tipo='COMP').count(), 
        'especialidades': Especialidad.objects.all(), 'cursos': Curso.objects.all(), 'anios': Anio.objects.all(), 
        'preguntas': preguntas, 'query': query, 'origen': origen, 
        'tipos_data': tipos_data, 'notas_data': notas_data
    }
    return render(request, 'core/reportes.html', context)

@login_required
@docente_required
def eliminar_pregunta(request, pregunta_id):
    get_object_or_404(Pregunta, id=pregunta_id).delete()
    messages.success(request, "Pregunta eliminada exitosamente.")
    return redirect('ver_reportes')

@login_required
@docente_required
def editar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta actualizada correctamente.")
            return redirect('ver_reportes')
    else:
        form = PreguntaForm(instance=pregunta)
    return render(request, 'core/editar_pregunta.html', {'form': form, 'pregunta': pregunta})

def obtener_preguntas_examen(curso_id=None, anio_id=None, limite=20):
    preguntas_filtradas = Pregunta.objects.all()
    if curso_id: preguntas_filtradas = preguntas_filtradas.filter(curso_id=curso_id)
    if anio_id: preguntas_filtradas = preguntas_filtradas.filter(anio_id=anio_id)
    todas = list(preguntas_filtradas)
    if not todas and curso_id: todas = list(Pregunta.objects.filter(curso_id=curso_id))
    if not todas: todas = list(Pregunta.objects.all())
    if not todas: return []

    om = [p for p in todas if p.tipo == 'OM']
    corr = [p for p in todas if p.tipo in ['CORR', 'CORR_CAUSA', 'CORR_DEF']]
    vf = [p for p in todas if p.tipo == 'VF']
    comp = [p for p in todas if p.tipo == 'COMP']

    seleccionadas = []
    if om: seleccionadas.append(random.choice(om))
    if corr: seleccionadas.append(random.choice(corr))
    if vf: seleccionadas.append(random.choice(vf))
    if comp: seleccionadas.append(random.choice(comp))

    ids_seleccionados = [p.id for p in seleccionadas]
    restantes = [p for p in todas if p.id not in ids_seleccionados]
    faltan = limite - len(seleccionadas)
    if faltan > 0 and restantes: seleccionadas.extend(random.sample(restantes, min(faltan, len(restantes))))
    random.shuffle(seleccionadas)
    return seleccionadas

@login_required
@docente_required
def generar_examen(request):
    curso_id = request.GET.get('curso')
    anio_id = request.GET.get('anio')
    preguntas_examen = obtener_preguntas_examen(curso_id, anio_id, 20)
    if not preguntas_examen: return render(request, 'core/examen_generado.html', {'error': 'El banco de preguntas está vacío.'})
    return render_examen_resuelto(request, preguntas_examen, curso_id, anio_id)

@login_required
@docente_required
def generar_examen_manual(request):
    if request.method == 'POST':
        pregunta_ids = request.POST.getlist('preguntas_seleccionadas')
        if not pregunta_ids:
            messages.error(request, "No seleccionaste ninguna pregunta.")
            return redirect('ver_reportes')
        preguntas_examen = Pregunta.objects.filter(id__in=pregunta_ids)
        return render_examen_resuelto(request, preguntas_examen, None, None)
    return redirect('ver_reportes')

def render_examen_resuelto(request, preguntas_examen, curso_id, anio_id):
    preguntas_resueltas = []
    for p in preguntas_examen: preguntas_resueltas.append({'obj': p, 'acierto': True})
    return render(request, 'core/examen_generado.html', {
        'preguntas_resueltas': preguntas_resueltas, 'nota_final': 20, 'puntaje_obtenido': len(preguntas_examen), 'total_preguntas': len(preguntas_examen),
        'curso_obj': Curso.objects.get(id=curso_id) if curso_id else None, 'anio_obj': Anio.objects.get(id=anio_id) if anio_id else None
    })

@login_required
def rendir_examen(request):
    curso_id = request.GET.get('curso')
    anio_id = request.GET.get('anio')
    # NUEVO: Recibimos el tiempo del formulario (por defecto 30 mins)
    tiempo_minutos = int(request.GET.get('tiempo', 30)) 
    
    preguntas_examen = obtener_preguntas_examen(curso_id, anio_id, 20)
    if not preguntas_examen: return render(request, 'core/examen_generado.html', {'error': 'No hay preguntas registradas.'})
        
    distractores = ["Ninguna de las anteriores", "Opción incorrecta", "Concepto no relacionado", "Definición errónea"]
    preguntas_renderizadas = []
    for p in preguntas_examen:
        opciones_corr = []
        if p.tipo.startswith('CORR'):
            opciones_corr = list(p.contenido.get('pares', {}).values())
            opciones_corr.append(random.choice(distractores))
            random.shuffle(opciones_corr)
        preguntas_renderizadas.append({'obj': p, 'opciones_corr': opciones_corr})
    
    return render(request, 'core/rendir_examen.html', {
        'preguntas': preguntas_renderizadas, 
        'curso_obj': Curso.objects.filter(id=curso_id).first() if curso_id else None, 
        'anio_obj': Anio.objects.filter(id=anio_id).first() if anio_id else None,
        'tiempo_minutos': tiempo_minutos # NUEVO: Enviamos el tiempo al HTML
    })

@login_required
def calificar_examen(request):
    if request.method == 'POST':
        pregunta_ids = request.POST.getlist('pregunta_ids')
        puntaje = 0
        resultados = []
        
        for p_id in pregunta_ids:
            p = Pregunta.objects.get(id=p_id)
            correcta = False
            respuesta_alumno, respuesta_correcta = "", ""
            
            if p.tipo == 'OM':
                opcion_id = request.POST.get(f'om_{p.id}')
                if opcion_id:
                    opcion_sel = Opcion.objects.get(id=opcion_id)
                    respuesta_alumno = opcion_sel.texto
                    opcion_correcta = p.opciones.filter(es_correcta=True).first()
                    if opcion_correcta:
                        respuesta_correcta = opcion_correcta.texto
                        if opcion_sel.es_correcta: correcta = True
            elif p.tipo.startswith('CORR'):
                aciertos_corr = 0
                pares = p.contenido.get('pares', {})
                for i, (clave, valor_correcto) in enumerate(pares.items()):
                    resp = request.POST.get(f'corr_{p.id}_{i}', '').strip().lower()
                    if resp == valor_correcto.strip().lower(): aciertos_corr += 1
                if aciertos_corr == len(pares) and len(pares) > 0: correcta = True
                respuesta_alumno = f"{aciertos_corr}/{len(pares)} correctas"
                respuesta_correcta = "Emparejamiento completo"
            elif p.tipo == 'VF':
                respuesta_alumno = request.POST.get(f'vf_{p.id}')
                es_vf_correcta = p.contenido.get('correcta', False)
                respuesta_correcta = "Verdadero" if es_vf_correcta else "Falso"
                if (respuesta_alumno == 'true' and es_vf_correcta) or (respuesta_alumno == 'false' and not es_vf_correcta): correcta = True
            elif p.tipo == 'COMP':
                respuesta_alumno = request.POST.get(f'comp_{p.id}', '').strip().lower()
                respuesta_correcta = p.contenido.get('palabra', '')
                if respuesta_alumno == respuesta_correcta.strip().lower(): correcta = True
            
            if correcta: puntaje += 1
            resultados.append({'pregunta': p, 'respuesta_alumno': respuesta_alumno, 'respuesta_correcta': respuesta_correcta, 'acierto': correcta})
            
        nota_final = (puntaje / len(pregunta_ids)) * 20 if pregunta_ids else 0
        
        if pregunta_ids:
            primera_pregunta = Pregunta.objects.get(id=pregunta_ids[0])
            ResultadoExamen.objects.create(
                alumno=request.user, curso=primera_pregunta.curso, anio=primera_pregunta.anio, seccion=primera_pregunta.seccion, nota=round(nota_final, 2)
            )
        
        return render(request, 'core/resultado_examen.html', {
            'resultados': resultados, 'nota_final': round(nota_final), 'puntaje': puntaje, 'total': len(pregunta_ids)
        })
    return redirect('home')

@login_required
@docente_required
def ver_historial_notas(request):
    notas = ResultadoExamen.objects.all().order_by('-fecha_rendido')
    from django.db.models import Avg
    notas_por_curso = ResultadoExamen.objects.values('curso__nombre').annotate(promedio=Avg('nota')).order_by('-promedio')[:5]
    notas_data = {'labels': [item['curso__nombre'] for item in notas_por_curso], 'values': [round(item['promedio'], 2) for item in notas_por_curso]}
    return render(request, 'core/historial_notas.html', {'notas': notas, 'notas_data': notas_data})

# ... (tus funciones de exportar excel se mantienen igual) ...
def estilizar_excel(ws, headers):
    header_font = Font(color="FFFFFF", bold=True, size=12)
    header_fill = PatternFill(start_color="0B2545", end_color="0B2545", fill_type="solid")
    alignment = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    ws.append(headers)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font, cell.fill, cell.alignment, cell.border = header_font, header_fill, alignment, border

@login_required
@docente_required
def exportar_preguntas_excel(request):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Banco de Preguntas"
    headers = ['ID', 'Tipo', 'Especialidad', 'Curso', 'Año', 'Sección', 'Enunciado', 'Creado por', 'Fecha']
    estilizar_excel(ws, headers)
    for p in Pregunta.objects.all().order_by('id'):
        ws.append([p.id, p.get_tipo_display(), p.curso.especialidad.nombre, p.curso.nombre, p.anio.get_numero_display(), p.seccion.letra, p.enunciado, p.creado_por.username if p.creado_por else "N/A", p.fecha_creacion.strftime("%d/%m/%Y %H:%M")])
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Banco_de_Preguntas_CITEN.xlsx"'
    wb.save(response); return response

@login_required
@docente_required
def exportar_notas_excel(request):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Historial de Notas"
    headers = ['Fecha', 'Alumno', 'Curso', 'Especialidad', 'Año', 'Sección', 'Nota Final']
    estilizar_excel(ws, headers)
    for n in ResultadoExamen.objects.all().order_by('-fecha_rendido'):
        ws.append([n.fecha_rendido.strftime("%d/%m/%Y %H:%M"), n.alumno.username, n.curso.nombre, n.curso.especialidad.nombre, n.anio.get_numero_display(), n.seccion.letra if n.seccion else "N/A", n.nota])
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Historial_de_Notas_CITEN.xlsx"'
    wb.save(response); return response