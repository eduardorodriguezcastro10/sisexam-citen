from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Procesos
    path('procesos/registrar/', views.registrar_pregunta, name='registrar_pregunta'),
    path('procesos/subir-material/', views.subir_material, name='subir_material'), 
    
    # Reportes y Exámenes
    path('reportes/', views.ver_reportes, name='ver_reportes'),
    path('reportes/historial-notas/', views.ver_historial_notas, name='ver_historial_notas'),
    
    # Exportar a Excel
    path('reportes/exportar-preguntas/', views.exportar_preguntas_excel, name='exportar_preguntas_excel'),
    path('reportes/exportar-notas/', views.exportar_notas_excel, name='exportar_notas_excel'),
    
    # CRUD Preguntas
    path('reportes/eliminar/<int:pregunta_id>/', views.eliminar_pregunta, name='eliminar_pregunta'),
    path('reportes/editar/<int:pregunta_id>/', views.editar_pregunta, name='editar_pregunta'),
    
    # Generación de Exámenes
    path('reportes/generar-examen/', views.generar_examen, name='generar_examen'),
    path('reportes/generar-examen-manual/', views.generar_examen_manual, name='generar_examen_manual'),
    path('reportes/rendir-examen/', views.rendir_examen, name='rendir_examen'),
    path('reportes/calificar-examen/', views.calificar_examen, name='calificar_examen'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)