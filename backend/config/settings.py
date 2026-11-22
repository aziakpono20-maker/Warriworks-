import os
from pathlib import Path
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() == 'true'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'unsafe-development-key-change-before-deploy'
    else:
        raise RuntimeError('DJANGO_SECRET_KEY must be set when DEBUG is false.')
ALLOWED_HOSTS = [
    x.strip()
    for x in os.getenv(
        'DJANGO_ALLOWED_HOSTS',
        'localhost,127.0.0.1,super-duper-adventure-5gpq4x66qxxgf4pqq-8000.app.github.dev'
    ).split(',')
    if x.strip()
]
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
INSTALLED_APPS = [
 'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
 'rest_framework','corsheaders','django_filters','apps.accounts','apps.marketplace','apps.workflow','apps.verification',
]
MIDDLEWARE = [
 'django.middleware.security.SecurityMiddleware','corsheaders.middleware.CorsMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default': {'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('POSTGRES_DB','warriworks'),'USER':os.getenv('POSTGRES_USER','warriworks'),'PASSWORD':os.getenv('POSTGRES_PASSWORD','warriworks'),'HOST':os.getenv('POSTGRES_HOST','localhost'),'PORT':os.getenv('POSTGRES_PORT','5432')}}
if os.getenv('DJANGO_USE_SQLITE','false').lower() == 'true':
 DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
AUTH_USER_MODEL='accounts.User'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'; TIME_ZONE='Africa/Lagos'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'; STATIC_ROOT=BASE_DIR/'staticfiles'; MEDIA_URL='media/'; MEDIA_ROOT=BASE_DIR/'media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
CORS_ALLOWED_ORIGINS = [
    x.strip()
    for x in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if x.strip()
]

CSRF_TRUSTED_ORIGINS = [
    x.strip()
    for x in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if x.strip()
]
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticatedOrReadOnly'],'DEFAULT_FILTER_BACKENDS':['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter'],'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination','PAGE_SIZE':20}
SESSION_COOKIE_HTTPONLY=True; SESSION_COOKIE_SAMESITE='Lax'; CSRF_COOKIE_SAMESITE='Lax'; SECURE_CONTENT_TYPE_NOSNIFF=True; X_FRAME_OPTIONS='DENY'
if not DEBUG:
 SECURE_SSL_REDIRECT=True; SESSION_COOKIE_SECURE=True; CSRF_COOKIE_SECURE=True; SECURE_HSTS_SECONDS=31536000; SECURE_HSTS_INCLUDE_SUBDOMAINS=True
PASSWORD_HASHERS=['django.contrib.auth.hashers.PBKDF2PasswordHasher','django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher','apps.accounts.hashers.WerkzeugScryptPasswordHasher']

CORS_ALLOW_CREDENTIALS=True
