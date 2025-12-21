"""
Django settings for temis project.
"""
import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'config.admin.CustomAdminConfig',  # Кастомный AdminConfig для группировки
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'ckeditor',
    'ckeditor_uploader',
    'content',
    'quizzes',
    'booking',
    'moyklass',
    'telegram',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Настройка базы данных
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor настройки
CKEDITOR_UPLOAD_PATH = 'uploads/'
# Используем CDN для CKEditor 4.25.1-lts (последняя безопасная версия)
# Примечание: django-ckeditor 6.7.3 поставляется с CKEditor 4.22.1, но мы можем переопределить через CDN
CKEDITOR_CDN_URL = 'https://cdn.ckeditor.com/4.25.1-lts/standard-all/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Image', 'Table', 'HorizontalRule', 'VideoEmbed'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
        ],
        'toolbar': 'Custom',
        'language': 'ru',
        # Разрешаем iframe и div для вставки видео
        'allowedContent': True,
        'extraPlugins': 'videoembed',
        # Настройки для iframe
        'extraAllowedContent': 'div[style];iframe[src,style,allowfullscreen,allow,frameborder]',
        # Указываем путь к локальным плагинам (для videoembed)
        'pluginsPath': '/static/ckeditor/ckeditor/plugins/',
    },
}

# Домен API для замены localhost в URL изображений
API_DOMAIN = config('API_DOMAIN', default='api.dev.logoped-spb.pro')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://temis.ooo",
    "http://temis.ooo",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF настройки для работы с HTTPS
CSRF_TRUSTED_ORIGINS = [
    "https://api.temis.ooo",
    "https://temis.ooo",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

# Настройки безопасности для HTTPS
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False  # Nginx уже обрабатывает редирект
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Настройки кэша для отслеживания отправленных уведомлений
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Настройки логирования
# Создаем директорию для логов, если её нет
logs_dir = BASE_DIR / 'logs'
try:
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = logs_dir / 'django.log'
except (OSError, PermissionError):
    # Если не удалось создать директорию (например, в CI/CD), используем только консоль
    log_file_path = None

# Настраиваем handlers
handlers_config = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
}

# Добавляем файловый handler только если директория создана
if log_file_path:
    handlers_config['file'] = {
        'class': 'logging.FileHandler',
        'filename': str(log_file_path),
        'formatter': 'verbose',
    }

# Определяем, какие handlers использовать
if log_file_path:
    root_handlers = ['console', 'file']
    django_handlers = ['console', 'file']
    moyklass_handlers = ['console', 'file']
else:
    root_handlers = ['console']
    django_handlers = ['console']
    moyklass_handlers = ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': handlers_config,
    'root': {
        'handlers': root_handlers,
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': django_handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'moyklass': {
            'handlers': moyklass_handlers,
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

