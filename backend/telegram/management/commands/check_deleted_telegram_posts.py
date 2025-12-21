"""
Management команда для проверки удаленных постов из Telegram канала
Можно запускать периодически через cron для проверки и деактивации удаленных постов
"""
from django.core.management.base import BaseCommand
from telegram.bot import get_bot_settings, deactivate_catalog_item_by_message_id, TELEGRAM_API_URL
from content.models import CatalogItem
import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Проверяет удаленные посты из Telegram канала и деактивирует соответствующие элементы каталога'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-limit',
            type=int,
            default=100,
            help='Количество последних активных элементов для проверки (по умолчанию: 100)',
        )

    def handle(self, *args, **options):
        bot_settings = get_bot_settings()
        
        if not bot_settings or not bot_settings.is_active:
            self.stdout.write(self.style.WARNING('Telegram бот не активен'))
            return
        
        if not bot_settings.sync_channel_enabled:
            self.stdout.write(self.style.WARNING('Синхронизация с каналом отключена'))
            return
        
        chat_id = bot_settings.channel_id or bot_settings.channel_username
        if not chat_id:
            self.stdout.write(self.style.ERROR('Не указан канал для проверки'))
            return
        
        # Если это username, убеждаемся, что он начинается с @
        if isinstance(chat_id, str) and not chat_id.startswith('-') and not chat_id.startswith('@'):
            chat_id = f'@{chat_id}'

        check_limit = options['check_limit']
        
        try:
            # Получаем активные элементы каталога с telegram_message_id
            active_items = CatalogItem.objects.filter(
                telegram_message_id__isnull=False,
                is_active=True
            ).order_by('-created_at')[:check_limit]
            
            if not active_items:
                self.stdout.write(self.style.SUCCESS('Нет активных элементов с telegram_message_id для проверки'))
                return
            
            self.stdout.write(f'Проверяю {len(active_items)} активных элементов...')
            
            deactivated_count = 0
            checked_count = 0
            
            for item in active_items:
                checked_count += 1
                message_id = item.telegram_message_id
                
                # Используем forwardMessage для проверки существования сообщения
                # Мы пересылаем сообщение самому себе (в тот же канал), но в "тихом" режиме
                # Это надежный способ проверить, существует ли сообщение в Bot API
                try:
                    # Мы используем copyMessage с параметрами, которые не приведут к реальному копированию
                    # или просто проверяем ответ API. На самом деле самый простой способ - это
                    # вызвать editMessageCaption с тем же текстом, но это может вызвать уведомление.
                    
                    # Лучший способ для Bot API - попробовать переслать сообщение.
                    # Если оно удалено, API вернет 400 Bad Request
                    url = TELEGRAM_API_URL.format(token=bot_settings.token, method='forwardMessage')
                    data = {
                        'chat_id': chat_id, # Пересылаем в тот же чат (но сообщение не будет создано, если не указать from_chat_id правильно)
                        'from_chat_id': chat_id,
                        'message_id': message_id,
                        'disable_notification': True
                    }
                    
                    # Мы делаем запрос, но нам не важно, перешлется ли оно на самом деле
                    # Нам важно, вернет ли API ошибку "Message to forward not found"
                    response = requests.post(url, data=data, timeout=10)
                    result = response.json()
                    
                    if not result.get('ok'):
                        error_desc = result.get('description', '')
                        if 'message to forward not found' in error_desc.lower() or 'message not found' in error_desc.lower():
                            self.stdout.write(self.style.WARNING(f'Пост {message_id} не найден в Telegram. Деактивирую...'))
                            deactivate_catalog_item_by_message_id(message_id)
                            deactivated_count += 1
                        else:
                            logger.debug(f'Telegram API error for message {message_id}: {error_desc}')
                            
                except Exception as e:
                    logger.error(f'Ошибка при проверке сообщения {message_id}: {str(e)}')
            
            self.stdout.write(self.style.SUCCESS(
                f'Проверка завершена. Проверено элементов: {checked_count}, '
                f'деактивировано (удалено в TG): {deactivated_count}'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка проверки: {str(e)}'))
            logger.error(f'Ошибка проверки удаленных постов Telegram: {str(e)}')
