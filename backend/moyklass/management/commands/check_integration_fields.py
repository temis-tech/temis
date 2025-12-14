"""
Команда для проверки полей интеграции MoyKlass
"""
from django.core.management.base import BaseCommand
from moyklass.models import MoyKlassIntegration
from booking.models import BookingForm


class Command(BaseCommand):
    help = 'Проверяет поля интеграции MoyKlass'

    def add_arguments(self, parser):
        parser.add_argument(
            '--integration-id',
            type=int,
            help='ID интеграции для проверки',
        )

    def handle(self, *args, **options):
        integration_id = options.get('integration_id')
        
        if integration_id:
            try:
                integration = MoyKlassIntegration.objects.select_related(
                    'booking_form', 'quiz'
                ).prefetch_related(
                    'booking_form__fields', 'quiz__questions'
                ).get(id=integration_id)
                
                self.stdout.write(self.style.SUCCESS(f'\n=== Интеграция #{integration.id} ==='))
                self.stdout.write(f'Тип источника: {integration.get_source_type_display()}')
                
                if integration.source_type == 'booking_form' and integration.booking_form:
                    self.stdout.write(f'\nФорма записи: {integration.booking_form.title} (ID: {integration.booking_form.id})')
                    form_fields = integration.booking_form.fields.all().order_by('order', 'id')
                    self.stdout.write(f'Количество полей: {form_fields.count()}')
                    
                    if form_fields.exists():
                        self.stdout.write('\nПоля формы:')
                        for field in form_fields:
                            self.stdout.write(
                                f'  - {field.label} ({field.name}) - '
                                f'{field.get_field_type_display()}'
                                f'{" [обязательное]" if field.is_required else ""}'
                            )
                    else:
                        self.stdout.write(self.style.WARNING('  В форме нет полей!'))
                
                elif integration.source_type == 'quiz' and integration.quiz:
                    self.stdout.write(f'\nАнкета: {integration.quiz.title} (ID: {integration.quiz.id})')
                    questions = integration.quiz.questions.all().order_by('order', 'id')
                    self.stdout.write(f'Количество вопросов: {questions.count()}')
                    
                    self.stdout.write('\nПоля анкеты:')
                    self.stdout.write('  - Имя пользователя (user_name)')
                    self.stdout.write('  - Телефон пользователя (user_phone)')
                    self.stdout.write('  - Email пользователя (user_email)')
                    
                    if questions.exists():
                        self.stdout.write('\nВопросы анкеты:')
                        for question in questions:
                            self.stdout.write(
                                f'  - {question.text[:50]}... (question_{question.id}) - '
                                f'{question.get_question_type_display()}'
                            )
                    else:
                        self.stdout.write(self.style.WARNING('  В анкете нет вопросов!'))
                
                # Проверяем маппинги
                mappings = integration.field_mappings.all().order_by('order', 'id')
                self.stdout.write(f'\nМаппинги полей: {mappings.count()}')
                if mappings.exists():
                    for mapping in mappings:
                        self.stdout.write(
                            f'  - {mapping.get_moyklass_field_display()} ← '
                            f'{mapping.source_field_name}'
                            f'{" [обязательное]" if mapping.is_required else ""}'
                        )
                else:
                    self.stdout.write(self.style.WARNING('  Нет маппингов полей!'))
                
            except MoyKlassIntegration.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Интеграция с ID {integration_id} не найдена')
                )
        else:
            # Показываем все интеграции
            integrations = MoyKlassIntegration.objects.select_related(
                'booking_form', 'quiz'
            ).all()
            
            self.stdout.write(self.style.SUCCESS(f'\n=== Всего интеграций: {integrations.count()} ===\n'))
            
            for integration in integrations:
                self.stdout.write(f'Интеграция #{integration.id}:')
                self.stdout.write(f'  Тип: {integration.get_source_type_display()}')
                if integration.booking_form:
                    self.stdout.write(f'  Форма: {integration.booking_form.title}')
                    form_fields = integration.booking_form.fields.count()
                    self.stdout.write(f'  Поля формы: {form_fields}')
                elif integration.quiz:
                    self.stdout.write(f'  Анкета: {integration.quiz.title}')
                    questions = integration.quiz.questions.count()
                    self.stdout.write(f'  Вопросов: {questions}')
                mappings = integration.field_mappings.count()
                self.stdout.write(f'  Маппингов: {mappings}')
                self.stdout.write('')
