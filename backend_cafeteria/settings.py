"""
Django settings for backend_cafeteria project.
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv # <-- AÑADIMOS ESTA LIBRERÍA

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 1. ESTO CARGA TU ARCHIVO .env LOCAL AUTOMÁTICAMENTE
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 2. AHORA LEEMOS LA CLAVE EXACTA QUE TIENES EN TU .ENV
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave-de-respaldo-por-si-acaso')

# 3. MANTENEMOS LA SEGURIDAD DINÁMICA
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*']

# ... (El resto del archivo queda exactamente igual que el que te pasé antes) ...

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones de terceros
    'corsheaders',
    'rest_framework',
    
    # Tus aplicaciones
    'productos',
    'ventas',
    'empleados',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Sirve los archivos estáticos en Render
    'corsheaders.middleware.CorsMiddleware',      # Permite la conexión con tu frontend (Vite)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de CORS para permitir que el frontend se comunique con la API
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'backend_cafeteria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend_cafeteria.wsgi.application'


# Database
# Lee la URL de conexión de Supabase desde las variables de entorno de Render
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
        ssl_require=False if 'RENDER' not in os.environ else True
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'es-bo'  # Configurado para español de Bolivia

TIME_ZONE = 'America/La_Paz' # Zona horaria local

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Directorio donde Render agrupará los archivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')