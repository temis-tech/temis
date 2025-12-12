"""
Константы для приложения
"""
from django.conf import settings

# Пути API
API_PREFIX = '/api'
MEDIA_PATH = '/media'

# Пути для различных эндпоинтов
TELEGRAM_WEBHOOK_PATH = f'{API_PREFIX}/telegram/webhook/'
MOYKLASS_WEBHOOK_PATH = f'{API_PREFIX}/moyklass/webhook/'

# Получить домен API из настроек
def get_api_domain():
    """Возвращает домен API из настроек"""
    return getattr(settings, 'API_DOMAIN', 'api.dev.logoped-spb.pro')

# Получить протокол (https/http) в зависимости от DEBUG
def get_protocol():
    """Возвращает протокол (https или http) в зависимости от DEBUG"""
    return 'https' if not getattr(settings, 'DEBUG', False) else 'http'

# Получить базовый URL API
def get_api_base_url():
    """Возвращает базовый URL API (протокол + домен + префикс)"""
    protocol = get_protocol()
    domain = get_api_domain()
    return f'{protocol}://{domain}{API_PREFIX}'

# Получить базовый URL для медиа файлов
def get_media_base_url():
    """Возвращает базовый URL для медиа файлов"""
    protocol = get_protocol()
    domain = get_api_domain()
    return f'{protocol}://{domain}{MEDIA_PATH}'
