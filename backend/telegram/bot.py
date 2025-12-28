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


def send_message(chat_id, text, parse_mode='HTML', reply_markup=None, keyboard=None):
    """
    Отправить сообщение пользователю
    
    Args:
        chat_id: ID чата (telegram_id пользователя)
        text: Текст сообщения
        parse_mode: Режим парсинга (HTML или Markdown)
        reply_markup: Inline клавиатура (опционально)
        keyboard: Reply клавиатура (постоянные кнопки внизу, опционально)
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.is_active:
        logger.debug('Telegram бот не активен')
        return False
    
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='sendMessage')
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    # Приоритет: reply_markup (inline) > keyboard (reply)
    if reply_markup:
        payload['reply_markup'] = reply_markup
    elif keyboard:
        payload['reply_markup'] = keyboard
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка отправки сообщения в Telegram: {str(e)}')
        return False


def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """
    Ответить на callback query
    
    Args:
        callback_query_id: ID callback query
        text: Текст ответа (опционально)
        show_alert: Показать alert вместо уведомления
    """
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.is_active:
        return False
    
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='answerCallbackQuery')
    
    payload = {
        'callback_query_id': callback_query_id
    }
    
    if text:
        payload['text'] = text
    if show_alert:
        payload['show_alert'] = True
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка ответа на callback query: {str(e)}')
        return False


def edit_message_text(chat_id, message_id, text, parse_mode='HTML', reply_markup=None):
    """
    Редактировать текст сообщения
    
    Args:
        chat_id: ID чата
        message_id: ID сообщения
        text: Новый текст
        parse_mode: Режим парсинга
        reply_markup: Inline клавиатура (опционально)
    """
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.is_active:
        return False
    
    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='editMessageText')
    
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка редактирования сообщения: {str(e)}')
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
        
        # Обрабатываем callback_query (нажатия на кнопки)
        callback_query = update_data.get('callback_query')
        if callback_query:
            handle_callback_query(callback_query)
            return
        
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
            )
            if user.is_admin:
                welcome_text += '📋 <b>Используйте кнопки ниже для работы с CRM</b>'
                # Создаем клавиатуру с кнопками CRM
                keyboard = {
                    'inline_keyboard': [
                        [
                            {'text': '📋 Необработанные заявки', 'callback_data': 'crm_leads'},
                            {'text': '🆕 Новые заявки', 'callback_data': 'crm_leads_new'}
                        ],
                        [
                            {'text': '⚙️ Заявки в работе', 'callback_data': 'crm_leads_in_progress'},
                            {'text': '👥 Клиенты', 'callback_data': 'crm_clients'}
                        ],
                        [
                            {'text': '🔄 Обновить', 'callback_data': 'crm_refresh'}
                        ]
                    ]
                }
                send_message(telegram_id, welcome_text, reply_markup=keyboard)
            else:
                welcome_text += 'Для получения уведомлений обратитесь к администратору.'
                send_message(telegram_id, welcome_text)
        
        # Обработка команд CRM (только для админов)
        elif user.is_admin:
            handle_crm_commands(telegram_id, text, user)
        
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


def handle_menu_button(telegram_id, text, user):
    """
    Обработать нажатие на кнопку меню
    
    Args:
        telegram_id: ID пользователя Telegram
        text: Текст кнопки
        user: Объект TelegramUser
    """
    try:
        from crm.models import Lead, Client, LeadStatus
        
        # Обрабатываем нажатия на кнопки меню
        if text == '📋 Необработанные заявки':
            show_leads_list(telegram_id)
        elif text == '🆕 Новые заявки':
            show_leads_list(telegram_id, status_code='new')
        elif text == '⚙️ Заявки в работе':
            show_leads_list(telegram_id, status_code='in_progress')
        elif text == '👥 Клиенты':
            show_clients_list(telegram_id)
        elif text == '🔄 Обновить меню':
            show_main_menu(telegram_id)
        else:
            # Если это не кнопка меню, проверяем старые команды для совместимости
            handle_crm_commands(telegram_id, text, user)
            
    except Exception as e:
        logger.error(f'Ошибка обработки кнопки меню: {str(e)}', exc_info=True)
        send_message(telegram_id, f'❌ Ошибка обработки: {str(e)}')


def handle_crm_commands(telegram_id, text, user):
    """
    Обработать команды CRM (для совместимости со старыми командами)
    
    Args:
        telegram_id: ID пользователя Telegram
        text: Текст команды
        user: Объект TelegramUser
    """
    try:
        from crm.models import Lead, Client, LeadStatus
        
        # Команда /leads - список необработанных заявок (новые и в работе)
        if text == '/leads' or text.startswith('/leads '):
            show_leads_list(telegram_id)
        
        # Команда /leads_new - только новые заявки
        elif text == '/leads_new':
            show_leads_list(telegram_id, status_code='new')
        
        # Команда /leads_in_progress - заявки в работе
        elif text == '/leads_in_progress':
            show_leads_list(telegram_id, status_code='in_progress')
        
        # Команда /client <id> - информация о клиенте
        elif text.startswith('/client '):
            try:
                client_id = int(text.split()[1])
                client = Client.objects.get(id=client_id)
                
                name = client.get_name() or 'Не указано'
                phone = client.get_phone() or 'Не указано'
                email = client.get_email() or 'Не указано'
                notes = client.notes or 'Нет заметок'
                created = client.created_at.strftime('%d.%m.%Y %H:%M')
                
                # Получаем файлы клиента
                files = client.files.all()[:10]
                files_text = ''
                if files:
                    files_text = '\n\n📎 <b>Файлы:</b>\n'
                    for file in files:
                        files_text += f'• {file.get_display_name()}\n'
                else:
                    files_text = '\n\n📎 Файлов нет'
                
                message = (
                    f'👤 <b>Клиент #{client.id}</b>\n\n'
                    f'<b>Имя:</b> {name}\n'
                    f'<b>Телефон:</b> {phone}\n'
                    f'<b>Email:</b> {email}\n'
                    f'<b>Создан:</b> {created}\n'
                    f'<b>Заметки:</b> {notes}'
                    f'{files_text}'
                )
                
                send_message(telegram_id, message)
            except (ValueError, IndexError):
                send_message(telegram_id, '❌ Неверный формат команды. Используйте: /client <id>')
            except Client.DoesNotExist:
                send_message(telegram_id, f'❌ Клиент с ID {client_id} не найден.')
            except Exception as e:
                logger.error(f'Ошибка получения информации о клиенте: {str(e)}')
                send_message(telegram_id, f'❌ Ошибка получения информации о клиенте: {str(e)}')
        
    except Exception as e:
        logger.error(f'Ошибка обработки команды CRM: {str(e)}', exc_info=True)
        send_message(telegram_id, f'❌ Ошибка обработки команды: {str(e)}')


def handle_callback_query(callback_query):
    """
    Обработать callback query (нажатие на кнопку)
    
    Args:
        callback_query: Данные callback query от Telegram
    """
    try:
        from telegram.models import TelegramUser
        from crm.models import Lead, Client, LeadStatus
        
        callback_data = callback_query.get('data', '')
        from_user = callback_query.get('from', {})
        telegram_id = from_user.get('id')
        message = callback_query.get('message', {})
        message_id = message.get('message_id')
        chat_id = message.get('chat', {}).get('id')
        callback_query_id = callback_query.get('id')
        
        # Получаем пользователя
        user = TelegramUser.objects.filter(telegram_id=telegram_id, is_admin=True, is_active=True).first()
        if not user:
            answer_callback_query(callback_query_id, '❌ У вас нет доступа к CRM', show_alert=True)
            return
        
        # Обрабатываем разные типы callback_data
        if callback_data == 'crm_leads':
            show_leads_list(chat_id, message_id, callback_query_id)
        elif callback_data == 'crm_leads_new':
            show_leads_list(chat_id, message_id, callback_query_id, status_code='new')
        elif callback_data == 'crm_leads_in_progress':
            show_leads_list(chat_id, message_id, callback_query_id, status_code='in_progress')
        elif callback_data == 'crm_clients':
            show_clients_list(chat_id, message_id, callback_query_id)
        elif callback_data == 'crm_refresh':
            show_main_menu(chat_id, message_id, callback_query_id)
        elif callback_data.startswith('crm_lead_'):
            # Просмотр деталей лида: crm_lead_<id>
            lead_id = callback_data.replace('crm_lead_', '')
            show_lead_details(chat_id, message_id, callback_query_id, lead_id)
        elif callback_data.startswith('crm_set_status_'):
            # Изменение статуса: crm_set_status_<lead_id>_<status_code>
            parts = callback_data.replace('crm_set_status_', '').split('_')
            if len(parts) >= 2:
                lead_id = parts[0]
                status_code = '_'.join(parts[1:])
                set_lead_status(chat_id, message_id, callback_query_id, lead_id, status_code)
        elif callback_data.startswith('crm_client_'):
            # Просмотр деталей клиента: crm_client_<id>
            client_id = callback_data.replace('crm_client_', '')
            show_client_details(chat_id, message_id, callback_query_id, client_id)
        else:
            answer_callback_query(callback_query_id, '❌ Неизвестная команда', show_alert=False)
            
    except Exception as e:
        logger.error(f'Ошибка обработки callback query: {str(e)}', exc_info=True)
        if 'callback_query_id' in locals():
            answer_callback_query(callback_query_id, '❌ Ошибка обработки', show_alert=True)


def show_main_menu(chat_id, message_id=None, callback_query_id=None):
    """Показать главное меню CRM"""
    text = '📋 <b>CRM - Главное меню</b>\n\nВыберите действие:'
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '📋 Необработанные заявки', 'callback_data': 'crm_leads'},
                {'text': '🆕 Новые заявки', 'callback_data': 'crm_leads_new'}
            ],
            [
                {'text': '⚙️ Заявки в работе', 'callback_data': 'crm_leads_in_progress'},
                {'text': '👥 Клиенты', 'callback_data': 'crm_clients'}
            ],
            [
                {'text': '🔄 Обновить', 'callback_data': 'crm_refresh'}
            ]
        ]
    }
    
    if message_id and callback_query_id:
        edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        answer_callback_query(callback_query_id, '✅ Обновлено')
    else:
        send_message(chat_id, text, reply_markup=keyboard)


def show_leads_list(chat_id, message_id=None, callback_query_id=None, status_code=None):
    """Показать список лидов"""
    try:
        from crm.models import Lead, LeadStatus
        
        if status_code:
            status = LeadStatus.objects.filter(code=status_code).first()
            if not status:
                if callback_query_id:
                    answer_callback_query(callback_query_id, f'❌ Статус "{status_code}" не найден', show_alert=True)
                return
            leads = Lead.objects.filter(status=status).order_by('-created_at')[:20]
            title = f'📋 {status.name}'
        else:
            # Необработанные (новые и в работе)
            new_status = LeadStatus.objects.filter(code='new').first()
            in_progress_status = LeadStatus.objects.filter(code='in_progress').first()
            statuses = [s for s in [new_status, in_progress_status] if s]
            if not statuses:
                if callback_query_id:
                    answer_callback_query(callback_query_id, '❌ Статусы не настроены', show_alert=True)
                return
            leads = Lead.objects.filter(status__in=statuses).order_by('-created_at')[:20]
            title = '📋 Необработанные заявки'
        
        if not leads:
            text = f'{title}\n\n✅ Нет заявок.'
            if message_id:
                # Для callback используем inline кнопку
                inline_keyboard = {
                    'inline_keyboard': [
                        [{'text': '🔙 Назад', 'callback_data': 'crm_refresh'}]
                    ]
                }
                edit_message_text(chat_id, message_id, text, reply_markup=inline_keyboard)
            else:
                send_message(chat_id, text, keyboard=menu_keyboard)
            if callback_query_id:
                answer_callback_query(callback_query_id, '✅ Нет заявок')
            return
        
        text = f'{title} ({leads.count()}):\n\n'
        buttons = []
        
        for lead in leads[:10]:  # Показываем первые 10
            name = lead.get_name() or 'Без имени'
            phone = lead.get_phone() or 'Нет телефона'
            status_name = lead.status.name if lead.status else 'Без статуса'
            created = lead.created_at.strftime('%d.%m.%Y %H:%M')
            text += (
                f'<b>#{lead.id}</b> {name}\n'
                f'📞 {phone} | 📊 {status_name}\n'
                f'📅 {created}\n\n'
            )
            buttons.append([{'text': f'#{lead.id} {name}', 'callback_data': f'crm_lead_{lead.id}'}])
        
        buttons.append([{'text': '🔙 Назад', 'callback_data': 'crm_refresh'}])
        
        keyboard = {'inline_keyboard': buttons}
        
        if message_id:
            edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            send_message(chat_id, text, reply_markup=keyboard)
        
        if callback_query_id:
            answer_callback_query(callback_query_id, f'✅ Найдено {leads.count()} заявок')
            
    except Exception as e:
        logger.error(f'Ошибка показа списка лидов: {str(e)}', exc_info=True)
        if callback_query_id:
            answer_callback_query(callback_query_id, '❌ Ошибка', show_alert=True)


def show_lead_details(chat_id, message_id, callback_query_id, lead_id):
    """Показать детали лида с кнопками изменения статуса"""
    try:
        from crm.models import Lead, LeadStatus
        
        lead = Lead.objects.get(id=lead_id)
        statuses = LeadStatus.objects.filter(is_active=True).exclude(code='converted').order_by('order')
        
        name = lead.get_name() or 'Не указано'
        phone = lead.get_phone() or 'Не указано'
        email = lead.get_email() or 'Не указано'
        status_name = lead.status.name if lead.status else 'Без статуса'
        created = lead.created_at.strftime('%d.%m.%Y %H:%M')
        source = lead.source or 'Не указан'
        notes = lead.notes or 'Нет заметок'
        
        text = (
            f'📋 <b>Лид #{lead.id}</b>\n\n'
            f'<b>Имя:</b> {name}\n'
            f'<b>Телефон:</b> {phone}\n'
            f'<b>Email:</b> {email}\n'
            f'<b>Статус:</b> {status_name}\n'
            f'<b>Источник:</b> {source}\n'
            f'<b>Создан:</b> {created}\n'
            f'<b>Заметки:</b> {notes}'
        )
        
        # Кнопки для изменения статуса
        buttons = []
        status_row = []
        for status in statuses:
            if lead.status and status.id == lead.status.id:
                status_row.append({'text': f'✅ {status.name}', 'callback_data': f'crm_set_status_{lead_id}_{status.code}'})
            else:
                status_row.append({'text': status.name, 'callback_data': f'crm_set_status_{lead_id}_{status.code}'})
            
            if len(status_row) >= 2:
                buttons.append(status_row)
                status_row = []
        
        if status_row:
            buttons.append(status_row)
        
        buttons.append([{'text': '🔙 Назад к списку', 'callback_data': 'crm_leads'}])
        
        keyboard = {'inline_keyboard': buttons}
        
        edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        answer_callback_query(callback_query_id, '✅')
        
    except Lead.DoesNotExist:
        answer_callback_query(callback_query_id, '❌ Лид не найден', show_alert=True)
    except Exception as e:
        logger.error(f'Ошибка показа деталей лида: {str(e)}', exc_info=True)
        answer_callback_query(callback_query_id, '❌ Ошибка', show_alert=True)


def set_lead_status(chat_id, message_id, callback_query_id, lead_id, status_code):
    """Изменить статус лида"""
    try:
        from crm.models import Lead, LeadStatus
        
        lead = Lead.objects.get(id=lead_id)
        status = LeadStatus.objects.filter(code=status_code).first()
        
        if not status:
            answer_callback_query(callback_query_id, '❌ Статус не найден', show_alert=True)
            return
        
        lead.status = status
        lead.save()
        
        # Показываем обновленные детали
        show_lead_details(chat_id, message_id, callback_query_id, lead_id)
        answer_callback_query(callback_query_id, f'✅ Статус изменен на "{status.name}"')
        
    except Lead.DoesNotExist:
        answer_callback_query(callback_query_id, '❌ Лид не найден', show_alert=True)
    except Exception as e:
        logger.error(f'Ошибка изменения статуса: {str(e)}', exc_info=True)
        answer_callback_query(callback_query_id, '❌ Ошибка', show_alert=True)


def show_clients_list(chat_id, message_id=None, callback_query_id=None):
    """Показать список клиентов"""
    try:
        from crm.models import Client
        
        clients = Client.objects.filter(is_active=True).order_by('-created_at')[:20]
        
        if not clients:
            text = '👥 <b>Клиенты</b>\n\n✅ Нет клиентов.'
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔙 Назад', 'callback_data': 'crm_refresh'}]
                ]
            }
            if message_id:
                edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
            else:
                send_message(chat_id, text, keyboard=get_crm_menu_keyboard())
            if callback_query_id:
                answer_callback_query(callback_query_id, '✅ Нет клиентов')
            return
        
        text = f'👥 <b>Клиенты ({clients.count()}):</b>\n\n'
        buttons = []
        
        for client in clients[:10]:
            name = client.get_name() or 'Без имени'
            phone = client.get_phone() or 'Нет телефона'
            created = client.created_at.strftime('%d.%m.%Y %H:%M')
            text += (
                f'<b>#{client.id}</b> {name}\n'
                f'📞 {phone} | 📅 {created}\n\n'
            )
            buttons.append([{'text': f'#{client.id} {name}', 'callback_data': f'crm_client_{client.id}'}])
        
        buttons.append([{'text': '🔙 Назад', 'callback_data': 'crm_refresh'}])
        
        keyboard = {'inline_keyboard': buttons}
        
        if message_id:
            edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            send_message(chat_id, text, reply_markup=keyboard)
        
        if callback_query_id:
            answer_callback_query(callback_query_id, f'✅ Найдено {clients.count()} клиентов')
            
    except Exception as e:
        logger.error(f'Ошибка показа списка клиентов: {str(e)}', exc_info=True)
        if callback_query_id:
            answer_callback_query(callback_query_id, '❌ Ошибка', show_alert=True)


def show_client_details(chat_id, message_id, callback_query_id, client_id):
    """Показать детали клиента"""
    try:
        from crm.models import Client
        
        client = Client.objects.get(id=client_id)
        
        name = client.get_name() or 'Не указано'
        phone = client.get_phone() or 'Не указано'
        email = client.get_email() or 'Не указано'
        created = client.created_at.strftime('%d.%m.%Y %H:%M')
        notes = client.notes or 'Нет заметок'
        
        # Получаем файлы клиента
        files = client.files.all()[:10]
        files_text = ''
        if files:
            files_text = '\n\n📎 <b>Файлы:</b>\n'
            for file in files:
                files_text += f'• {file.get_display_name()}\n'
        else:
            files_text = '\n\n📎 Файлов нет'
        
        text = (
            f'👤 <b>Клиент #{client.id}</b>\n\n'
            f'<b>Имя:</b> {name}\n'
            f'<b>Телефон:</b> {phone}\n'
            f'<b>Email:</b> {email}\n'
            f'<b>Создан:</b> {created}\n'
            f'<b>Заметки:</b> {notes}'
            f'{files_text}'
        )
        
        keyboard = {
            'inline_keyboard': [
                [{'text': '🔙 Назад к списку', 'callback_data': 'crm_clients'}]
            ]
        }
        
        edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        answer_callback_query(callback_query_id, '✅')
        
    except Client.DoesNotExist:
        answer_callback_query(callback_query_id, '❌ Клиент не найден', show_alert=True)
    except Exception as e:
        logger.error(f'Ошибка показа деталей клиента: {str(e)}', exc_info=True)
        answer_callback_query(callback_query_id, '❌ Ошибка', show_alert=True)

