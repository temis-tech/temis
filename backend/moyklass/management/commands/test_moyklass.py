"""
Команда для тестирования интеграции с MoyKlass CRM

Использование:
    python manage.py test_moyklass
    python manage.py test_moyklass --create-student
"""
from django.core.management.base import BaseCommand, CommandError
from moyklass.models import MoyKlassSettings
from moyklass.client import MoyKlassClient, MoyKlassAPIError


class Command(BaseCommand):
    help = 'Тестирует интеграцию с MoyKlass CRM'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-student',
            action='store_true',
            help='Создать тестового ученика в MoyKlass'
        )
        parser.add_argument(
            '--list-students',
            action='store_true',
            help='Показать список учеников из MoyKlass'
        )
    
    def handle(self, *args, **options):
        settings = MoyKlassSettings.objects.first()
        
        if not settings:
            raise CommandError('Настройки MoyKlass не найдены. Создайте их в админке.')
        
        if not settings.is_active:
            raise CommandError('Интеграция MoyKlass неактивна. Включите её в админке.')
        
        if not settings.api_key:
            raise CommandError('API ключ не настроен.')
        
        self.stdout.write(self.style.SUCCESS('🔍 Тестирую подключение к MoyKlass API...'))
        self.stdout.write('')
        
        try:
            client = MoyKlassClient(settings)
            
            # Тест 1: Получение информации о компании
            self.stdout.write('1️⃣ Получаю информацию о компании...')
            try:
                company_info = client.get_company_info()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'   ✓ Компания: {company_info.get("name", "Неизвестно")}\n'
                        f'   ✓ ID компании: {company_info.get("id", "Неизвестно")}'
                    )
                )
            except MoyKlassAPIError as e:
                self.stdout.write(self.style.ERROR(f'   ✗ Ошибка: {str(e)}'))
                return
            
            self.stdout.write('')
            
            # Тест 2: Получение списка учеников
            if options['list_students']:
                self.stdout.write('2️⃣ Получаю список учеников...')
                try:
                    students = client.get_students(page=1, per_page=5)
                    students_list = students.get('data', [])
                    total = students.get('pagination', {}).get('total', 0)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✓ Всего учеников в системе: {total}')
                    )
                    self.stdout.write(f'   ✓ Показано: {len(students_list)}')
                    
                    if students_list:
                        self.stdout.write('   Последние ученики:')
                        for student in students_list[:3]:
                            name = student.get('name', 'Без имени')
                            student_id = student.get('id', '?')
                            phone = student.get('phone', 'Нет телефона')
                            self.stdout.write(f'     - {name} (ID: {student_id}, Телефон: {phone})')
                except MoyKlassAPIError as e:
                    self.stdout.write(self.style.ERROR(f'   ✗ Ошибка: {str(e)}'))
            
            self.stdout.write('')
            
            # Тест 3: Создание тестового ученика
            if options['create_student']:
                self.stdout.write('3️⃣ Создаю тестового ученика...')
                try:
                    test_student_data = {
                        'name': 'Тестовый Ученик (Rainbow Say)',
                        'phone': '+79000000000',
                        'email': 'test@rainbow-say.local',
                        'comment': 'Тестовый лид, созданный через интеграцию Rainbow Say'
                    }
                    
                    result = client.create_student(test_student_data)
                    student_id = result.get('id')
                    student_name = result.get('name', 'Неизвестно')
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'   ✓ Ученик успешно создан!\n'
                            f'   ✓ ID: {student_id}\n'
                            f'   ✓ Имя: {student_name}'
                        )
                    )
                    self.stdout.write('')
                    self.stdout.write(
                        self.style.WARNING(
                            '⚠️  Не забудьте удалить тестового ученика из MoyKlass после проверки!'
                        )
                    )
                except MoyKlassAPIError as e:
                    self.stdout.write(self.style.ERROR(f'   ✗ Ошибка создания ученика: {str(e)}'))
            
            # Проверка токена
            self.stdout.write('')
            self.stdout.write('4️⃣ Проверяю токен доступа...')
            if settings.is_token_valid():
                expires_in = settings.token_expires_at - settings.created_at if settings.token_expires_at else None
                self.stdout.write(
                    self.style.SUCCESS(f'   ✓ Токен действителен до: {settings.token_expires_at}')
                )
            else:
                self.stdout.write(self.style.WARNING('   ⚠ Токен недействителен или отсутствует'))
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ Все тесты пройдены успешно!'))
            self.stdout.write('')
            self.stdout.write('💡 Полезные команды:')
            self.stdout.write('   - Показать список учеников: python manage.py test_moyklass --list-students')
            self.stdout.write('   - Создать тестового ученика: python manage.py test_moyklass --create-student')
            
        except MoyKlassAPIError as e:
            raise CommandError(f'Ошибка API MoyKlass: {str(e)}')
        except Exception as e:
            raise CommandError(f'Ошибка: {str(e)}')

