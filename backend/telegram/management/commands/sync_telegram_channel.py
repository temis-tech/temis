"""
Management команда для синхронизации постов из Telegram канала
Можно запускать периодически через cron для получения постов, которые могли быть пропущены
"""
from django.core.management.base import BaseCommand
from telegram.bot import get_bot_settings, get_file_from_telegram, create_catalog_item_from_telegram_post
from telegram.models import TelegramBotSettings
import requests
import logging

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = 'https://api.telegram.org/bot{token}/{method}'


class Command(BaseCommand):
    help = 'Синхронизирует посты из Telegram канала и создает элементы каталога'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Максимальное количество постов для синхронизации (по умолчанию: 10)',
        )

    def handle(self, *args, **options):
        bot_settings = get_bot_settings()
        
        if not bot_settings or not bot_settings.is_active:
            self.stdout.write(self.style.WARNING('Telegram бот не активен'))
            return
        
        if not bot_settings.sync_channel_enabled:
            self.stdout.write(self.style.WARNING('Синхронизация с каналом отключена'))
            return
        
        if not bot_settings.channel_username and not bot_settings.channel_id:
            self.stdout.write(self.style.ERROR('Не указан канал для синхронизации'))
            return
        
        if not bot_settings.catalog_page:
            self.stdout.write(self.style.ERROR('Не указана страница каталога для создания элементов'))
            return
        
        limit = options['limit']
        
        try:
            # Получаем обновления из канала
            url = TELEGRAM_API_URL.format(token=bot_settings.token, method='getUpdates')
            
            # Получаем последние обновления
            response = requests.post(url, json={
                'offset': -limit,  # Получаем последние N обновлений
                'allowed_updates': ['channel_post']  # Только посты из канала
            }, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get('ok'):
                self.stdout.write(self.style.ERROR(f'Ошибка API Telegram: {data}'))
                return
            
            updates = data.get('result', [])
            created_count = 0
            
            for update in updates:
                channel_post = update.get('channel_post')
                if channel_post:
                    # Проверяем соответствие канала
                    chat = channel_post.get('chat', {})
                    chat_id = str(chat.get('id', ''))
                    chat_username = chat.get('username', '')
                    
                    channel_match = False
                    if bot_settings.channel_id and chat_id == bot_settings.channel_id:
                        channel_match = True
                    elif bot_settings.channel_username:
                        username_clean = bot_settings.channel_username.lstrip('@')
                        if chat_username == username_clean:
                            channel_match = True
                            # Сохраняем ID канала
                            if not bot_settings.channel_id:
                                bot_settings.channel_id = chat_id
                                bot_settings.save(update_fields=['channel_id'])
                    
                    if channel_match:
                        catalog_item = create_catalog_item_from_telegram_post(channel_post)
                        if catalog_item:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f'Создан элемент каталога: {catalog_item.title}'))
            
            self.stdout.write(self.style.SUCCESS(f'Синхронизация завершена. Создано элементов каталога: {created_count}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка синхронизации: {str(e)}'))
            logger.error(f'Ошибка синхронизации Telegram канала: {str(e)}')
