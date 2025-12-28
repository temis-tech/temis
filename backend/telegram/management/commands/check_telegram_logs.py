"""
Команда для проверки последних логов Telegram
"""
from django.core.management.base import BaseCommand
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Проверяет последние логи Telegram из файлов логов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lines',
            type=int,
            default=100,
            help='Количество строк для вывода (по умолчанию: 100)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Проверять логи за последние N часов (по умолчанию: 24)'
        )

    def handle(self, *args, **options):
        lines = options['lines']
        hours = options['hours']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Проверка логов Telegram'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        # Проверяем логи из systemd journal
        self.stdout.write('\n📋 Проверка логов из systemd journal:')
        self.stdout.write('-' * 80)
        
        # Пытаемся прочитать логи из journalctl
        import subprocess
        try:
            # Получаем логи за последние N часов
            since_time = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
            cmd = [
                'journalctl',
                '-u', 'temis-backend',
                '--since', since_time,
                '--no-pager',
                '-n', str(lines)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Фильтруем только логи, связанные с Telegram
                telegram_lines = []
                for line in result.stdout.split('\n'):
                    if any(keyword in line.lower() for keyword in ['telegram', 'catalog', 'hashtag', 'webhook', 'error', 'exception']):
                        telegram_lines.append(line)
                
                if telegram_lines:
                    self.stdout.write('\n'.join(telegram_lines))
                else:
                    self.stdout.write(self.style.WARNING('Нет логов Telegram за указанный период'))
            else:
                self.stdout.write(self.style.ERROR(f'Ошибка выполнения journalctl: {result.stderr}'))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING('journalctl не найден, пропускаем проверку systemd логов'))
        except subprocess.TimeoutExpired:
            self.stdout.write(self.style.ERROR('Таймаут при чтении логов'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка чтения логов: {str(e)}'))
        
        # Проверяем файлы логов Django
        self.stdout.write('\n📋 Проверка файлов логов Django:')
        self.stdout.write('-' * 80)
        
        log_files = [
            '/var/log/temis-backend-error.log',
            '/var/log/temis-backend-access.log',
            '/var/www/temis/backend/logs/telegram.log',
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                self.stdout.write(f'\n📄 {log_file}:')
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        all_lines = f.readlines()
                        # Берем последние строки
                        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                        # Фильтруем только Telegram-связанные
                        telegram_lines = [
                            line for line in recent_lines
                            if any(keyword in line.lower() for keyword in ['telegram', 'catalog', 'hashtag', 'webhook', 'error', 'exception'])
                        ]
                        if telegram_lines:
                            self.stdout.write(''.join(telegram_lines))
                        else:
                            self.stdout.write(self.style.WARNING('  Нет записей, связанных с Telegram'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Ошибка чтения файла: {str(e)}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Файл не найден: {log_file}'))
        
        # Проверяем настройки бота
        self.stdout.write('\n📋 Проверка настроек Telegram бота:')
        self.stdout.write('-' * 80)
        
        try:
            from telegram.models import TelegramBotSettings, TelegramHashtagMapping
            
            bot_settings = TelegramBotSettings.objects.first()
            if bot_settings:
                self.stdout.write(f'  Активен: {bot_settings.is_active}')
                self.stdout.write(f'  Синхронизация канала включена: {bot_settings.sync_channel_enabled}')
                self.stdout.write(f'  ID канала: {bot_settings.channel_id or "не указан"}')
                self.stdout.write(f'  Username канала: {bot_settings.channel_username or "не указан"}')
                self.stdout.write(f'  Webhook URL: {bot_settings.webhook_url or "не установлен"}')
            else:
                self.stdout.write(self.style.ERROR('  Настройки бота не найдены!'))
            
            hashtag_mappings = TelegramHashtagMapping.objects.filter(is_active=True)
            self.stdout.write(f'\n  Активных настроек хештегов: {hashtag_mappings.count()}')
            for mapping in hashtag_mappings:
                self.stdout.write(f'    - #{mapping.hashtag} → {mapping.catalog_page.title if mapping.catalog_page else "не указана страница"}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Ошибка проверки настроек: {str(e)}'))
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('Проверка завершена'))
        self.stdout.write('=' * 80)

