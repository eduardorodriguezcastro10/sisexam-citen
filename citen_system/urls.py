from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Gestión de Usuarios
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/carga-masiva/', views.cargar_usuarios_excel, name='cargar_usuarios_excel'),
    
    # Procesos
    path('procesos/registrar/', views.registrar_pregunta, name='registrar_pregunta'),
    path('procesos/subir-material/', views.subir_material, name='subir_material'),
    
    # Bancos de Preguntas
    path('bancos/', views.bancos_preguntas, name='bancos_preguntas'),
    path('bancos/subir/', views.subir_banco_excel, name='subir_banco_excel'),
    path('bancos/procesar/<str:nombre_archivo>/', views.procesar_banco_excel, name='procesar_banco_excel'),
    path('bancos/eliminar/<str:nombre_archivo>/', views.eliminar_banco_excel, name='eliminar_banco_excel'),
    path('bancos/ver/<str:nombre_archivo>/', views.ver_preguntas_banco, name='ver_preguntas_banco'), 
    path('bancos/generar-examen-avanzado/', views.generar_examen_porcentajes, name='generar_examen_porcentajes'),
    path('bancos/examen/<int:examen_id>/resultados/', views.ver_resultados_examen, name='ver_resultados_examen'),
    
    # Reportes
    path('reportes/', views.ver_reportes, name='ver_reportes'),
    path('reportes/historial-notas/', views.ver_historial_notas, name='ver_historial_notas'),
    path('reportes/eliminar/<int:pregunta_id>/', views.eliminar_pregunta, name='eliminar_pregunta'),
    path('reportes/editar/<int:pregunta_id>/', views.editar_pregunta, name='editar_pregunta'),
    
    # Revisión de Libres
    path('reportes/revisar-libres/<int:resultado_id>/', views.revisar_libres, name='revisar_libres'),
    path('reportes/guardar-libres/<int:resultado_id>/', views.guardar_revision_libres, name='guardar_revision_libres'),
    
    # Exportaciones
    path('reportes/exportar-preguntas/', views.exportar_preguntas_excel, name='exportar_preguntas_excel'),
    path('reportes/exportar-notas/', views.exportar_notas_excel, name='exportar_notas_excel'),
    
    # Exámenes
    path('reportes/generar-examen/', views.generar_examen, name='generar_examen'),
    path('reportes/generar-examen-manual/', views.generar_examen_manual, name='generar_examen_manual'),
    path('reportes/rendir-examen/', views.rendir_examen, name='rendir_examen'),
    path('examen-asignado/<int:examen_id>/', views.rendir_examen_asignado, name='rendir_examen_asignado'),
    path('calificar-examen/', views.calificar_examen, name='calificar_examen'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Contraseñas
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset_form.html', email_template_name='core/password_reset_email.html', subject_template_name='core/password_reset_subject.txt', success_url='/password-reset/done/'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html', success_url='/login/'), name='password_reset_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)