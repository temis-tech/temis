"""
Команда для синхронизации данных с MoyKlass CRM

Использование:
    python manage.py sync_moyklass --type students
    python manage.py sync_moyklass --type payments
    python manage.py sync_moyklass --type bookings
    python manage.py sync_moyklass --all
"""
from django.core.management.base import BaseCommand, CommandError
from moyklass.models import MoyKlassSettings
from moyklass.sync import MoyKlassSync
from moyklass.client import MoyKlassAPIError


class Command(BaseCommand):
    help = 'Синхронизирует данные с MoyKlass CRM'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['students', 'payments', 'bookings', 'groups', 'lessons'],
            help='Тип данных для синхронизации'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Синхронизировать все включенные типы данных'
        )
    
    def handle(self, *args, **options):
        settings = MoyKlassSettings.objects.first()
        
        if not settings:
            raise CommandError('Настройки MoyKlass не найдены. Создайте их в админке.')
        
        if not settings.is_active:
            raise CommandError('Интеграция MoyKlass неактивна. Включите её в админке.')
        
        sync = MoyKlassSync(settings)
        
        try:
            if options['all']:
                self.stdout.write('Начинаю полную синхронизацию...')
                results = sync.sync_all()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nСинхронизация завершена:\n'
                        f'  Обработано: {results["total_processed"]}\n'
                        f'  Создано: {results["total_created"]}\n'
                        f'  Обновлено: {results["total_updated"]}\n'
                        f'  Ошибок: {results["total_errors"]}'
                    )
                )
                
            elif options['type']:
                sync_type = options['type']
                self.stdout.write(f'Начинаю синхронизацию {sync_type}...')
                
                if sync_type == 'students':
                    results = sync.sync_students()
                elif sync_type == 'payments':
                    results = sync.sync_payments()
                elif sync_type == 'bookings':
                    results = sync.sync_bookings()
                else:
                    raise CommandError(f'Синхронизация {sync_type} еще не реализована')
                
                if results.get('skipped'):
                    self.stdout.write(
                        self.style.WARNING(f'Синхронизация {sync_type} пропущена: {results.get("message")}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\nСинхронизация {sync_type} завершена:\n'
                            f'  Обработано: {results.get("processed", 0)}\n'
                            f'  Создано: {results.get("created", 0)}\n'
                            f'  Обновлено: {results.get("updated", 0)}\n'
                            f'  Ошибок: {results.get("errors", 0)}'
                        )
                    )
            else:
                raise CommandError('Укажите --type или --all')
                
        except MoyKlassAPIError as e:
            raise CommandError(f'Ошибка API MoyKlass: {str(e)}')
        except Exception as e:
            raise CommandError(f'Ошибка синхронизации: {str(e)}')

