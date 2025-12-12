"""
Логика для работы с Telegram ботом
"""
import requests
import logging
from django.conf import settings
from .models import TelegramBotSettings, TelegramUser

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = 'https://api.telegram.org/bot{token}/{method}'


def get_bot_settings():
    """Получить настройки бота"""
    return TelegramBotSettings.objects.first()


def send_message(chat_id, text, parse_mode='HTML'):
    """
    Отправить сообщение пользователю
    
    Args:
        chat_id: ID чата (telegram_id пользователя)
        text: Текст сообщения
        parse_mode: Режим парсинга (HTML или Markdown)
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.is_active:
        logger.debug('Telegram бот не активен')
        return False
    
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='sendMessage')
    
    try:
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }, timeout=10)
        
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка отправки сообщения в Telegram: {str(e)}')
        return False


def send_notification_to_admins(text):
    """
    Отправить уведомление всем админам
    
    Args:
        text: Текст уведомления
    
    Returns:
        int: Количество успешно отправленных уведомлений
    """
    admins = TelegramUser.objects.filter(is_admin=True, is_active=True)
    sent_count = 0
    
    for admin in admins:
        if send_message(admin.telegram_id, text):
            sent_count += 1
    
    return sent_count


def handle_webhook_update(update_data):
    """
    Обработать обновление от Telegram webhook
    
    Args:
        update_data: Данные обновления от Telegram
    """
    try:
        message = update_data.get('message')
        if not message:
            return
        
        from_user = message.get('from')
        if not from_user:
            return
        
        telegram_id = from_user.get('id')
        username = from_user.get('username', '')
        first_name = from_user.get('first_name', '')
        last_name = from_user.get('last_name', '')
        text = message.get('text', '')
        
        # Создаем или обновляем пользователя
        user, created = TelegramUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )
        
        if created:
            logger.info(f'Новый пользователь Telegram: {user}')
        
        # Отправляем приветственное сообщение
        if text in ['/start', '/help']:
            welcome_text = (
                '👋 Добро пожаловать!\n\n'
                'Этот бот отправляет уведомления о событиях на сайте.\n\n'
                'Для получения уведомлений обратитесь к администратору.'
            )
            send_message(telegram_id, welcome_text)
        
    except Exception as e:
        logger.error(f'Ошибка обработки webhook: {str(e)}')


def set_webhook(webhook_url):
    """
    Установить webhook для бота
    
    Args:
        webhook_url: URL для webhook
    
    Returns:
        bool: True если успешно
    """
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.is_active:
        return False
    
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='setWebhook')
    
    try:
        response = requests.post(url, json={
            'url': webhook_url
        }, timeout=10)
        
        # Логируем ответ для отладки
        logger.info(f'Telegram API response status: {response.status_code}')
        logger.info(f'Telegram API response: {response.text}')
        
        response.raise_for_status()
        
        # Сохраняем URL webhook в настройках
        bot_settings.webhook_url = webhook_url
        bot_settings.save(update_fields=['webhook_url'])
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка установки webhook: {str(e)}')
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f'Response status: {e.response.status_code}')
            logger.error(f'Response text: {e.response.text}')
        return False


def delete_webhook():
    """Удалить webhook для бота"""
    bot_settings = get_bot_settings()
    if not bot_settings:
        return False
    
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='deleteWebhook')
    
    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        
        bot_settings.webhook_url = ''
        bot_settings.save(update_fields=['webhook_url'])
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка удаления webhook: {str(e)}')
        return False

