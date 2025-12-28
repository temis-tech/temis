"""
Логика для работы с Telegram ботом
"""
import requests
import logging
import os
import tempfile
import re
from io import BytesIO
from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from django.utils.text import slugify
from .models import TelegramBotSettings, TelegramUser, TelegramSyncLog
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


def extract_hashtags(text):
    """
    Извлечь хештеги из текста
    
    Args:
        text: Текст поста
    
    Returns:
        list: Список хештегов без символа #
    """
    # Ищем хештеги (слово после #, может содержать буквы, цифры и подчеркивания)
    hashtags = re.findall(r'#(\w+)', text, re.UNICODE)
    # Приводим к нижнему регистру для сравнения
    return [tag.lower() for tag in hashtags]


def log_sync_event(event_type, status='success', message='', message_id=None, chat_id=None, 
                   chat_username=None, hashtags=None, catalog_item=None, error_details='', raw_data=None):
    """
    Сохранить лог события синхронизации
    
    Args:
        event_type: Тип события (из TelegramSyncLog.EVENT_TYPE_CHOICES)
        status: Статус ('success', 'error', 'warning', 'skipped')
        message: Сообщение о событии
        message_id: ID сообщения Telegram
        chat_id: ID канала
        chat_username: Username канала
        hashtags: Список хештегов или строка через запятую
        catalog_item: Объект CatalogItem
        error_details: Детали ошибки
        raw_data: Исходные данные из Telegram
    """
    try:
        hashtags_str = ', '.join(hashtags) if isinstance(hashtags, list) else (hashtags or '')
        
        log = TelegramSyncLog.objects.create(
            event_type=event_type,
            status=status,
            message=message,
            message_id=message_id,
            chat_id=str(chat_id) if chat_id else '',
            chat_username=chat_username or '',
            hashtags=hashtags_str,
            catalog_item=catalog_item,
            catalog_item_title=catalog_item.title if catalog_item else '',
            error_details=error_details,
            raw_data=raw_data
        )
        return log
    except Exception as e:
        # Обрабатываем ошибки, связанные с отсутствием таблицы (миграция еще не применена)
        error_str = str(e).lower()
        # Проверяем различные варианты ошибок отсутствия таблицы
        table_not_exists_patterns = [
            "doesn't exist",
            "does not exist",
            "no such table",
            "table.*doesn't exist",
            "relation.*does not exist",
            "unknown table"
        ]
        
        is_table_error = any(pattern in error_str for pattern in table_not_exists_patterns)
        
        if is_table_error:
            # Таблица еще не создана - это нормально до применения миграций
            logger.debug(f'Таблица TelegramSyncLog еще не создана (миграция не применена), пропускаем сохранение лога')
        else:
            # Другая ошибка - логируем
            logger.error(f'Ошибка сохранения лога синхронизации: {str(e)}', exc_info=True)
        return None


def find_hashtag_mapping(hashtags):
    """
    Найти настройку для хештега
    
    Args:
        hashtags: Список хештегов из поста
    
    Returns:
        TelegramHashtagMapping или None
    """
    from .models import TelegramHashtagMapping
    
    if not hashtags:
        return None
    
    # Ищем первую активную настройку для любого из хештегов
    for hashtag in hashtags:
        mapping = TelegramHashtagMapping.objects.filter(
            hashtag__iexact=hashtag,
            is_active=True
        ).first()
        if mapping:
            return mapping
    
    return None


def create_or_update_catalog_item_from_telegram_post(post_data, is_edit=False):
    """
    Создать или обновить элемент каталога из поста Telegram
    
    Args:
        post_data: Данные поста из Telegram (channel_post, edited_channel_post или message)
        is_edit: True если это обновление существующего поста
    
    Returns:
        CatalogItem: Созданный или обновленный элемент каталога или None
    """
    from content.utils.image_processing import process_uploaded_image
    from content.models import CatalogItem
    
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.sync_channel_enabled:
        return None
    
    try:
        message_id = post_data.get('message_id')
        if not message_id:
            logger.debug('Пост не содержит message_id, пропускаем')
            return None
        
        # Проверяем, существует ли уже элемент с таким message_id
        existing_item = None
        if message_id:
            try:
                existing_item = CatalogItem.objects.get(telegram_message_id=message_id)
            except CatalogItem.DoesNotExist:
                pass
        
        # Извлекаем текст поста
        text = post_data.get('text') or post_data.get('caption', '')
        if not text:
            logger.debug('Пост не содержит текста, пропускаем')
            return None
        
        # Извлекаем хештеги из текста
        hashtags = extract_hashtags(text)
        
        # Ищем настройку для хештега
        hashtag_mapping = find_hashtag_mapping(hashtags)
        
        if not hashtag_mapping:
            # Если это обновление и элемент уже существует, но хештег удален - удаляем элемент
            if is_edit and existing_item:
                logger.info(f'Хештег удален из поста {message_id}, элемент каталога будет деактивирован')
                existing_item.is_active = False
                existing_item.save(update_fields=['is_active'])
                log_sync_event(
                    event_type='catalog_item_deactivated',
                    status='success',
                    message=f'Элемент каталога деактивирован: хештег удален из поста',
                    message_id=message_id,
                    catalog_item=existing_item,
                    hashtags=hashtags
                )
            else:
                logger.debug(f'Не найдена настройка для хештегов: {hashtags}. Пост пропущен.')
                log_sync_event(
                    event_type='channel_post',
                    status='skipped',
                    message=f'Не найдена настройка для хештегов: {hashtags}',
                    message_id=message_id,
                    chat_id=post_data.get('chat', {}).get('id'),
                    chat_username=post_data.get('chat', {}).get('username'),
                    hashtags=hashtags,
                    raw_data=post_data
                )
            return None
        
        catalog_page = hashtag_mapping.catalog_page
        
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
        
        # Убираем хештеги из текста для заголовка и описания
        text_without_hashtags = text
        for hashtag in hashtags:
            # Удаляем хештег из текста (с # и без)
            text_without_hashtags = re.sub(rf'#{hashtag}\b', '', text_without_hashtags, flags=re.IGNORECASE)
        text_without_hashtags = text_without_hashtags.strip()
        
        # Разделяем текст на части, если указан разделитель
        full_description = text_without_hashtags
        if hashtag_mapping.preview_separator:
            # Используем разделитель
            parts = text_without_hashtags.split(hashtag_mapping.preview_separator, 1)
            if len(parts) == 2:
                # До разделителя - краткое описание (не используется для card_description)
                # После разделителя - полный текст
                full_description = parts[1].strip()
            # Если разделитель не найден, используем весь текст как полный
        
        # Создаем заголовок из первой строки или начала текста
        # Берем первую строку или первые 200 символов из исходного текста (до разделителя, если он есть)
        title_source = text_without_hashtags.split(hashtag_mapping.preview_separator, 1)[0] if hashtag_mapping.preview_separator else text_without_hashtags
        title = title_source.split('\n')[0] if title_source else ''
        title = title[:200] if len(title) > 200 else title
        # Убираем переносы строк для заголовка
        title = title.replace('\n', ' ').strip()
        if not title:
            title = 'Элемент из Telegram'
        
        # card_description всегда берется из полного текста (description),
        # обрезанный до длины заголовка
        title_length = len(title)
        if len(full_description) > title_length:
            # Берем текст из description длиной равной длине заголовка
            # Обрезаем по границе слова для читаемости
            card_description_text = full_description[:title_length]
            last_space = card_description_text.rfind(' ')
            if last_space > title_length * 0.7:  # Если пробел не слишком далеко от конца
                card_description = full_description[:last_space].strip()
            else:
                card_description = card_description_text.strip()
        else:
            card_description = full_description.strip()
        
        # Создаем slug
        slug_base = transliterate_slug(title) or f'telegram_post_{post_data.get("message_id", "unknown")}'
        
        # Проверяем, не существует ли уже элемент с таким slug
        slug = slug_base
        counter = 1
        while CatalogItem.objects.filter(slug=slug).exists():
            slug = f'{slug_base}_{counter}'
            counter += 1
        
        # Если элемент уже существует - обновляем его
        if existing_item:
            catalog_item = existing_item
            # Обновляем данные элемента
            catalog_item.page = catalog_page
            catalog_item.title = title
            catalog_item.card_description = card_description
            catalog_item.description = full_description
            catalog_item.width = hashtag_mapping.width
            catalog_item.has_own_page = hashtag_mapping.has_own_page
            catalog_item.image_position = hashtag_mapping.image_position
            catalog_item.image_target_width = hashtag_mapping.image_target_width
            catalog_item.image_target_height = hashtag_mapping.image_target_height
            catalog_item.button_type = hashtag_mapping.button_type
            catalog_item.button_text = hashtag_mapping.button_text or ''
            catalog_item.button_booking_form = hashtag_mapping.button_booking_form if hashtag_mapping.button_type == 'booking' else None
            catalog_item.button_quiz = hashtag_mapping.button_quiz if hashtag_mapping.button_type == 'quiz' else None
            if hashtag_mapping.button_type == 'external':
                catalog_item.button_url = str(hashtag_mapping.button_external_url) if hashtag_mapping.button_external_url else ''
            else:
                catalog_item.button_url = ''
            catalog_item.is_active = True
            # Сохраняем message_id если еще не сохранен
            if not catalog_item.telegram_message_id:
                catalog_item.telegram_message_id = message_id
        else:
            # Создаем новый элемент
            # Определяем порядок
            # Если в настройках указан order > 0, используем его как базовый
            # Иначе берем последний элемент + 1
            if hashtag_mapping.order > 0:
                # Ищем последний элемент с таким же или большим order
                last_item = CatalogItem.objects.filter(
                    page=catalog_page,
                    order__gte=hashtag_mapping.order
                ).order_by('-order').first()
                if last_item:
                    order = last_item.order + 1
                else:
                    order = hashtag_mapping.order
            else:
                # Используем порядок по умолчанию (в конец)
                last_item = CatalogItem.objects.filter(page=catalog_page).order_by('-order').first()
                order = (last_item.order + 1) if last_item else 0
            
            # Создаем элемент каталога с настройками из хештега
            catalog_item = CatalogItem(
                page=catalog_page,
                title=title,
                slug=slug,
                card_description=card_description,
                description=full_description,
                width=hashtag_mapping.width,
                has_own_page=hashtag_mapping.has_own_page,
                image_position=hashtag_mapping.image_position,
                image_target_width=hashtag_mapping.image_target_width,
                image_target_height=hashtag_mapping.image_target_height,
                button_type=hashtag_mapping.button_type,
                button_text=hashtag_mapping.button_text or '',
                button_booking_form=hashtag_mapping.button_booking_form if hashtag_mapping.button_type == 'booking' else None,
                button_quiz=hashtag_mapping.button_quiz if hashtag_mapping.button_type == 'quiz' else None,
                button_url=str(hashtag_mapping.button_external_url) if (hashtag_mapping.button_type == 'external' and hashtag_mapping.button_external_url) else '',
                order=order,
                is_active=True,
                telegram_message_id=message_id
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
        
        action = 'Обновлен' if existing_item else 'Создан'
        logger.info(f'{action} элемент каталога из Telegram поста с хештегом {hashtags}: {catalog_item.title}')
        
        # Сохраняем лог о создании/обновлении элемента
        event_type = 'catalog_item_updated' if existing_item else 'catalog_item_created'
        log_sync_event(
            event_type=event_type,
            status='success',
            message=f'{action} элемент каталога: {catalog_item.title}',
            message_id=message_id,
            chat_id=post_data.get('chat', {}).get('id'),
            chat_username=post_data.get('chat', {}).get('username'),
            hashtags=hashtags,
            catalog_item=catalog_item
        )
        
        return catalog_item
        
    except Exception as e:
        error_msg = f'Ошибка создания элемента каталога из Telegram поста: {str(e)}'
        logger.error(error_msg, exc_info=True)
        
        # Сохраняем лог об ошибке
        import traceback
        log_sync_event(
            event_type='error',
            status='error',
            message=error_msg,
            message_id=post_data.get('message_id'),
            chat_id=post_data.get('chat', {}).get('id'),
            chat_username=post_data.get('chat', {}).get('username'),
            hashtags=hashtags if 'hashtags' in locals() else None,
            error_details=traceback.format_exc(),
            raw_data=post_data
        )
        
        return None


def deactivate_catalog_item_by_message_id(message_id, chat_id=None):
    """
    Деактивировать элемент каталога по message_id из Telegram
    
    Args:
        message_id: ID сообщения из Telegram
        chat_id: ID чата/канала (опционально, для проверки)
    
    Returns:
        CatalogItem: Деактивированный элемент или None
    """
    from content.models import CatalogItem
    
    try:
        catalog_item = CatalogItem.objects.get(telegram_message_id=message_id)
        if catalog_item.is_active:
            catalog_item.is_active = False
            catalog_item.save(update_fields=['is_active'])
            logger.info(f'Элемент каталога деактивирован из-за удаления поста Telegram: {catalog_item.title} (message_id: {message_id})')
        else:
            logger.debug(f'Элемент каталога с message_id {message_id} уже деактивирован')
        return catalog_item
    except CatalogItem.DoesNotExist:
        logger.debug(f'Элемент каталога с message_id {message_id} не найден')
        return None
    except Exception as e:
        logger.error(f'Ошибка деактивации элемента каталога по message_id {message_id}: {str(e)}')
        return None


def handle_webhook_update(update_data):
    """
    Обработать обновление от Telegram webhook
    
    Args:
        update_data: Данные обновления от Telegram
    """
    try:
        bot_settings = get_bot_settings()
        
        if not bot_settings:
            logger.debug('Настройки Telegram бота не найдены')
            log_sync_event(
                event_type='warning',
                status='warning',
                message='Настройки Telegram бота не найдены',
                raw_data=update_data
            )
            return
        
        if not bot_settings.sync_channel_enabled:
            logger.debug('Синхронизация канала выключена в настройках')
            log_sync_event(
                event_type='warning',
                status='skipped',
                message='Синхронизация канала выключена в настройках',
                raw_data=update_data
            )
            return
        
        # Обрабатываем посты из канала (channel_post)
        channel_post = update_data.get('channel_post')
        if channel_post:
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
                logger.info(f'Канал совпадает, обрабатываем пост message_id: {channel_post.get("message_id")}')
                # Сохраняем лог о получении поста
                log_sync_event(
                    event_type='channel_post',
                    status='success',
                    message=f'Получен пост из канала',
                    message_id=channel_post.get('message_id'),
                    chat_id=chat_id,
                    chat_username=chat_username,
                    raw_data=channel_post
                )
                # Создаем элемент каталога из поста
                catalog_item = create_or_update_catalog_item_from_telegram_post(channel_post, is_edit=False)
                if catalog_item:
                    logger.info(f'Создан элемент каталога из Telegram канала: {catalog_item.title}')
                else:
                    logger.warning(f'Не удалось создать элемент каталога из поста message_id: {channel_post.get("message_id")}')
            else:
                logger.debug(f'Канал не совпадает: chat_id={chat_id}, username={chat_username}, ожидаемый channel_id={bot_settings.channel_id}, channel_username={bot_settings.channel_username}')
                log_sync_event(
                    event_type='channel_post',
                    status='skipped',
                    message=f'Канал не совпадает: chat_id={chat_id}, username={chat_username}',
                    message_id=channel_post.get('message_id'),
                    chat_id=chat_id,
                    chat_username=chat_username,
                    raw_data=channel_post
                )
        
        # Обрабатываем обновленные посты из канала (edited_channel_post)
        edited_channel_post = update_data.get('edited_channel_post')
        if edited_channel_post:
            # Проверяем, что пост из нужного канала
            chat = edited_channel_post.get('chat', {})
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
            
            if channel_match:
                logger.info(f'Получен обновленный пост из канала, обрабатываем message_id: {edited_channel_post.get("message_id")}')
                # Сохраняем лог о получении обновленного поста
                log_sync_event(
                    event_type='edited_channel_post',
                    status='success',
                    message=f'Получен обновленный пост из канала',
                    message_id=edited_channel_post.get('message_id'),
                    chat_id=chat_id,
                    chat_username=chat_username,
                    raw_data=edited_channel_post
                )
                # Обновляем элемент каталога из отредактированного поста
                catalog_item = create_or_update_catalog_item_from_telegram_post(edited_channel_post, is_edit=True)
                if catalog_item:
                    logger.info(f'Обновлен элемент каталога из Telegram канала: {catalog_item.title}')
                else:
                    logger.warning(f'Не удалось обновить элемент каталога из поста message_id: {edited_channel_post.get("message_id")}')
            else:
                logger.debug(f'Канал не совпадает для обновленного поста: chat_id={chat_id}, username={chat_username}, ожидаемый channel_id={bot_settings.channel_id}, channel_username={bot_settings.channel_username}')
                log_sync_event(
                    event_type='edited_channel_post',
                    status='skipped',
                    message=f'Канал не совпадает для обновленного поста: chat_id={chat_id}, username={chat_username}',
                    message_id=edited_channel_post.get('message_id'),
                    chat_id=chat_id,
                    chat_username=chat_username,
                    raw_data=edited_channel_post
                )
        
        # Обрабатываем удаленные сообщения из канала
        # Telegram Bot API не отправляет стандартные события об удалении через webhook,
        # но некоторые реализации или будущие версии API могут отправлять такие события.
        # Также обрабатываем случаи, когда приходит минимальная информация о сообщении
        # (только message_id без содержимого) - это может означать удаление.
        
        # Вариант 1: deleted_channel_post (если такой формат приходит)
        deleted_channel_post = update_data.get('deleted_channel_post')
        if deleted_channel_post and bot_settings and bot_settings.sync_channel_enabled:
            message_id = deleted_channel_post.get('message_id')
            if message_id:
                chat = deleted_channel_post.get('chat', {})
                chat_id = str(chat.get('id', ''))
                
                # Проверяем соответствие канала
                channel_match = False
                if bot_settings.channel_id and chat_id == bot_settings.channel_id:
                    channel_match = True
                elif bot_settings.channel_username:
                    chat_username = chat.get('username', '')
                    username_clean = bot_settings.channel_username.lstrip('@')
                    if chat_username == username_clean:
                        channel_match = True
                
                if channel_match:
                    deactivate_catalog_item_by_message_id(message_id, chat_id)
        
        # Вариант 2: message_deleted (если такой формат приходит)
        message_deleted = update_data.get('message_deleted')
        if message_deleted and bot_settings and bot_settings.sync_channel_enabled:
            chat_id = message_deleted.get('chat', {}).get('id')
            message_ids = message_deleted.get('message_ids', [])
            
            # Проверяем соответствие канала
            channel_match = False
            if bot_settings.channel_id and str(chat_id) == bot_settings.channel_id:
                channel_match = True
            
            if channel_match and message_ids:
                for msg_id in message_ids:
                    deactivate_catalog_item_by_message_id(msg_id, str(chat_id))
        
        # Вариант 3: channel_post с минимальной информацией (только message_id, без text/caption)
        # Это может означать, что сообщение было удалено или изменено так, что не содержит контента
        channel_post_minimal = update_data.get('channel_post')
        if (channel_post_minimal and bot_settings and bot_settings.sync_channel_enabled and
            channel_post_minimal.get('message_id') and
            not channel_post_minimal.get('text') and not channel_post_minimal.get('caption')):
            # Проверяем, что это действительно удаление, а не просто пост без текста
            # Если есть другие поля (photo, video и т.д.), это не удаление
            has_content = any(key in channel_post_minimal for key in ['photo', 'video', 'document', 'audio', 'voice', 'sticker'])
            if not has_content:
                message_id = channel_post_minimal.get('message_id')
                chat = channel_post_minimal.get('chat', {})
                chat_id = str(chat.get('id', ''))
                
                # Проверяем соответствие канала
                channel_match = False
                if bot_settings.channel_id and chat_id == bot_settings.channel_id:
                    channel_match = True
                elif bot_settings.channel_username:
                    chat_username = chat.get('username', '')
                    username_clean = bot_settings.channel_username.lstrip('@')
                    if chat_username == username_clean:
                        channel_match = True
                
                if channel_match:
                    # Деактивируем элемент, если он существует
                    deactivate_catalog_item_by_message_id(message_id, chat_id)
        
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

