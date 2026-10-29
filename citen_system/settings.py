"""
Django settings for citen_system project.
"""

from pathlib import Path
import os
import dj_database_url 
from dotenv import load_dotenv 

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = 'django-insecure-)nzu@#rq@&hhq3h3=e^lse4ig!jj0j2x0jz#+4@ipl^9m_6z)3'

# En tu PC será True. En PythonAnywhere lo cambiaremos a False.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Para los archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'citen_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'citen_system.wsgi.application'

# =======================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# =======================================================
# La magia está aquí: le decimos que si no encuentra una URL en internet, 
# use por defecto tu base de datos local (para que sigas trabajando en VS Code).
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:Elbatuterry12@localhost:5432/citen_db',
        conn_max_age=600,
        ssl_require=True
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-pe' 
TIME_ZONE = 'America/Lima' 
USE_I18N = True
USE_TZ = True

# =======================================================
# ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# =======================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles' 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Autenticación
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

# Claves de API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# Esto quita los avisos amarillos de la consola
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'