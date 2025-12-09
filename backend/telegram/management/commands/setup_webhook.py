"""
Management команда для установки webhook для Telegram бота
Использование: python manage.py setup_webhook
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.bot import set_webhook, get_bot_settings


class Command(BaseCommand):
    help = 'Устанавливает webhook для Telegram бота'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='URL для webhook (если не указан, будет использован API_DOMAIN из settings)',
        )

    def handle(self, *args, **options):
        bot_settings = get_bot_settings()
        if not bot_settings:
            self.stdout.write(self.style.ERROR('Настройки бота не найдены. Создайте их в админке.'))
            return
        
        if not bot_settings.is_active:
            self.stdout.write(self.style.WARNING('Бот неактивен. Включите его в админке.'))
            return
        
        # Определяем URL для webhook
        if options['url']:
            webhook_url = options['url']
        else:
            api_domain = getattr(settings, 'API_DOMAIN', 'api.rainbow-say.estenomada.es')
            protocol = 'https' if not settings.DEBUG else 'http'
            webhook_url = f'{protocol}://{api_domain}/api/telegram/webhook/'
        
        self.stdout.write(f'Устанавливаю webhook: {webhook_url}')
        
        if set_webhook(webhook_url):
            self.stdout.write(self.style.SUCCESS('Webhook успешно установлен!'))
        else:
            self.stdout.write(self.style.ERROR('Ошибка установки webhook. Проверьте токен и URL.'))

