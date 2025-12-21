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
    return getattr(settings, 'API_DOMAIN', 'api.temis.ooo')

# Получить протокол (https/http) в зависимости от DEBUG
def get_protocol():
    """Возвращает протокол (https или http) в зависимости от DEBUG"""
    # Для продакшена всегда используем HTTPS
    # Для локальной разработки можно использовать HTTP
    if getattr(settings, 'DEBUG', False):
        # Проверяем, не продакшен ли это (по домену)
        api_domain = get_api_domain()
        if 'temis.ooo' in api_domain:
            return 'https'  # Даже на dev используем HTTPS
        return 'http'  # Только для localhost
    return 'https'  # Продакшен всегда HTTPS

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

