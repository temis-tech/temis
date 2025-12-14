#!/usr/bin/env python
"""
Скрипт для отладки проблемы с полями интеграции MoyKlass
Запуск: python manage.py shell < check_integration_debug.py
Или: python manage.py shell, затем выполнить код вручную
"""
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from moyklass.models import MoyKlassIntegration, MoyKlassFieldMapping
from booking.models import BookingForm

print("=" * 80)
print("ПРОВЕРКА ИНТЕГРАЦИИ MOYKLASS")
print("=" * 80)

# Проверяем интеграцию с ID=2
integration_id = 2
try:
    integration = MoyKlassIntegration.objects.select_related(
        'booking_form', 'quiz'
    ).prefetch_related(
        'booking_form__fields', 'quiz__questions'
    ).get(id=integration_id)
    
    print(f"\n✓ Интеграция #{integration.id} найдена")
    print(f"  Тип источника: {integration.get_source_type_display()}")
    print(f"  Активна: {integration.is_active}")
    
    if integration.source_type == 'booking_form':
        if integration.booking_form:
            print(f"\n✓ Форма записи: {integration.booking_form.title} (ID: {integration.booking_form.id})")
            
            # Загружаем поля формы
            form_fields = integration.booking_form.fields.all().order_by('order', 'id')
            print(f"  Количество полей в БД: {form_fields.count()}")
            
            if form_fields.exists():
                print("\n  Поля формы:")
                for field in form_fields:
                    print(f"    - {field.label} ({field.name}) - {field.get_field_type_display()}")
            else:
                print("  ⚠ В форме НЕТ полей в БД!")
        else:
            print("\n✗ Форма записи не указана!")
    
    elif integration.source_type == 'quiz':
        if integration.quiz:
            print(f"\n✓ Анкета: {integration.quiz.title} (ID: {integration.quiz.id})")
            questions = integration.quiz.questions.all().order_by('order', 'id')
            print(f"  Количество вопросов: {questions.count()}")
        else:
            print("\n✗ Анкета не указана!")
    
    # Проверяем маппинги
    mappings = integration.field_mappings.all().order_by('order', 'id')
    print(f"\n  Маппингов полей: {mappings.count()}")
    if mappings.exists():
        for mapping in mappings:
            print(f"    - {mapping.get_moyklass_field_display()} ← {mapping.source_field_name}")
    
    # Проверяем, что integration доступен через связь
    print(f"\n  Проверка связей:")
    print(f"    integration.booking_form_id: {integration.booking_form_id}")
    print(f"    integration.quiz_id: {integration.quiz_id}")
    if integration.booking_form:
        print(f"    integration.booking_form: {integration.booking_form}")
        print(f"    integration.booking_form.fields.exists(): {integration.booking_form.fields.exists()}")
    
except MoyKlassIntegration.DoesNotExist:
    print(f"\n✗ Интеграция с ID {integration_id} не найдена!")
    print("\nДоступные интеграции:")
    for integration in MoyKlassIntegration.objects.all():
        print(f"  - ID: {integration.id}, Тип: {integration.get_source_type_display()}")
except Exception as e:
    print(f"\n✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
