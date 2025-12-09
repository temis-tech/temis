"""
Management команда для проверки и отправки уведомлений о баннерах
Запускать через cron каждую минуту: * * * * * python manage.py check_banners
"""
from django.core.management.base import BaseCommand
from telegram.signals import check_banner_notifications


class Command(BaseCommand):
    help = 'Проверяет и отправляет уведомления о начале/завершении отображения баннеров'

    def handle(self, *args, **options):
        try:
            check_banner_notifications()
            self.stdout.write(self.style.SUCCESS('Проверка баннеров завершена'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))

