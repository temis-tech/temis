"""
Логика для работы с Telegram ботом
"""
import requests
import logging
import os
import tempfile
from io import BytesIO
from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from django.utils.text import slugify
from .models import TelegramBotSettings, TelegramUser
from content.models import transliterate_slug, Article

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


def get_file_from_telegram(file_id):
    """
    Получить файл из Telegram по file_id
    
    Args:
        file_id: ID файла в Telegram
    
    Returns:
        bytes: Содержимое файла или None
    """
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.is_active:
        return None
    
    # Сначала получаем путь к файлу
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='getFile')
    try:
        response = requests.post(url, json={'file_id': file_id}, timeout=10)
        response.raise_for_status()
        file_data = response.json()
        
        if not file_data.get('ok'):
            logger.error(f'Ошибка получения файла: {file_data}')
            return None
        
        file_path = file_data['result']['file_path']
        
        # Скачиваем файл
        download_url = f'https://api.telegram.org/file/bot{bot_settings.token}/{file_path}'
        file_response = requests.get(download_url, timeout=30)
        file_response.raise_for_status()
        
        return file_response.content
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка получения файла из Telegram: {str(e)}')
        return None


def download_image_from_telegram(file_id, filename=None):
    """
    Скачать изображение из Telegram и вернуть как Django File
    
    Args:
        file_id: ID файла в Telegram
        filename: Имя файла (опционально)
    
    Returns:
        tuple: (Django File объект, имя файла) или (None, None)
    """
    file_content = get_file_from_telegram(file_id)
    if not file_content:
        return None, None
    
    if not filename:
        # Определяем расширение из содержимого или используем jpg по умолчанию
        filename = f'telegram_image_{file_id}.jpg'
    
    # Создаем временный файл
    temp_file = BytesIO(file_content)
    django_file = ImageFile(temp_file, name=filename)
    return django_file, filename


def create_catalog_item_from_telegram_post(post_data):
    """
    Создать элемент каталога из поста Telegram
    
    Args:
        post_data: Данные поста из Telegram (channel_post или message)
    
    Returns:
        CatalogItem: Созданный элемент каталога или None
    """
    from content.utils.image_processing import process_uploaded_image
    from content.models import CatalogItem
    
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.sync_channel_enabled:
        return None
    
    if not bot_settings.catalog_page:
        logger.warning('Не указана страница каталога для синхронизации Telegram')
        return None
    
    try:
        # Извлекаем текст поста
        text = post_data.get('text') or post_data.get('caption', '')
        if not text:
            logger.debug('Пост не содержит текста, пропускаем')
            return None
        
        # Извлекаем изображение
        image_file = None
        image_filename = None
        photo = post_data.get('photo')
        if photo:
            # Берем самое большое изображение (последнее в массиве)
            largest_photo = photo[-1] if isinstance(photo, list) else photo
            file_id = largest_photo.get('file_id')
            if file_id:
                image_file, image_filename = download_image_from_telegram(file_id)
        
        # Создаем заголовок из текста
        title = text[:200] if len(text) > 200 else text
        # Убираем переносы строк для заголовка
        title = title.replace('\n', ' ').strip()
        if not title:
            title = 'Элемент из Telegram'
        
        # Создаем slug
        slug_base = transliterate_slug(title) or f'telegram_post_{post_data.get("message_id", "unknown")}'
        
        # Проверяем, не существует ли уже элемент с таким slug
        slug = slug_base
        counter = 1
        while CatalogItem.objects.filter(slug=slug).exists():
            slug = f'{slug_base}_{counter}'
            counter += 1
        
        # Определяем порядок (последний элемент + 1)
        last_item = CatalogItem.objects.filter(page=bot_settings.catalog_page).order_by('-order').first()
        order = (last_item.order + 1) if last_item else 0
        
        # Создаем элемент каталога
        catalog_item = CatalogItem(
            page=bot_settings.catalog_page,
            title=title,
            slug=slug,
            card_description=text[:500] if len(text) > 500 else text,  # Краткое описание для карточки
            description=text,  # Полное описание для страницы
            has_own_page=True,  # По умолчанию создаем страницу для элемента
            button_type='none',  # По умолчанию без кнопки
            button_text='',
            order=order,
            is_active=True
        )
        
        # Сохраняем изображение для карточки (если есть)
        if image_file and image_filename:
            catalog_item.card_image.save(
                image_filename,
                image_file,
                save=False
            )
            # Также используем это изображение для страницы элемента
            catalog_item.image.save(
                image_filename,
                image_file,
                save=False
            )
        
        catalog_item.save()
        
        # Обрабатываем изображения после сохранения
        if catalog_item.card_image and hasattr(catalog_item.card_image, 'file'):
            try:
                process_uploaded_image(catalog_item.card_image, image_type='general')
                catalog_item.save(update_fields=['card_image'])
            except Exception as e:
                logger.error(f'Ошибка обработки изображения карточки для элемента {catalog_item.title}: {e}')
        
        if catalog_item.image and hasattr(catalog_item.image, 'file'):
            try:
                process_uploaded_image(catalog_item.image, image_type='general')
                catalog_item.save(update_fields=['image'])
            except Exception as e:
                logger.error(f'Ошибка обработки изображения страницы для элемента {catalog_item.title}: {e}')
        
        logger.info(f'Создан элемент каталога из Telegram поста: {catalog_item.title}')
        return catalog_item
        
    except Exception as e:
        logger.error(f'Ошибка создания статьи из Telegram поста: {str(e)}')
        return None


def handle_webhook_update(update_data):
    """
    Обработать обновление от Telegram webhook
    
    Args:
        update_data: Данные обновления от Telegram
    """
    try:
        bot_settings = get_bot_settings()
        
        # Обрабатываем посты из канала (channel_post)
        channel_post = update_data.get('channel_post')
        if channel_post and bot_settings and bot_settings.sync_channel_enabled:
            # Проверяем, что пост из нужного канала
            chat = channel_post.get('chat', {})
            chat_id = str(chat.get('id', ''))
            chat_username = chat.get('username', '')
            
            # Проверяем соответствие канала
            channel_match = False
            if bot_settings.channel_id and chat_id == bot_settings.channel_id:
                channel_match = True
            elif bot_settings.channel_username:
                # Убираем @ если есть
                username_clean = bot_settings.channel_username.lstrip('@')
                if chat_username == username_clean:
                    channel_match = True
                    # Сохраняем ID канала для будущих проверок
                    if not bot_settings.channel_id:
                        bot_settings.channel_id = chat_id
                        bot_settings.save(update_fields=['channel_id'])
            
            if channel_match:
                # Создаем элемент каталога из поста
                catalog_item = create_catalog_item_from_telegram_post(channel_post)
                if catalog_item:
                    logger.info(f'Создан элемент каталога из Telegram канала: {catalog_item.title}')
        
        # Обрабатываем обычные сообщения (для бота)
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

