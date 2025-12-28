from django.db.models.signals import post_save
from django.dispatch import receiver
from booking.models import BookingSubmission
from quizzes.models import QuizSubmission
from .models import Lead, LeadStatus


def extract_contact_data(data, field_mapping=None):
    """
    Извлечь контактные данные из JSON данных формы
    
    Args:
        data: Словарь с данными формы
        field_mapping: Словарь маппинга полей {'name': 'имя', 'phone': 'телефон', 'email': 'email'}
    
    Returns:
        dict: {'name': str, 'phone': str, 'email': str}
    """
    result = {
        'name': '',
        'phone': '',
        'email': ''
    }
    
    # Стандартные имена полей для поиска
    name_fields = ['name', 'имя', 'fio', 'фио', 'full_name', 'fullname']
    phone_fields = ['phone', 'телефон', 'tel', 'mobile', 'мобильный']
    email_fields = ['email', 'e-mail', 'mail', 'почта']
    
    # Если есть маппинг, используем его
    if field_mapping:
        for key, value in data.items():
            key_lower = key.lower()
            if key_lower in field_mapping.get('name', []):
                result['name'] = str(value).strip()
            elif key_lower in field_mapping.get('phone', []):
                result['phone'] = str(value).strip()
            elif key_lower in field_mapping.get('email', []):
                result['email'] = str(value).strip()
    else:
        # Автоматический поиск по стандартным именам
        for key, value in data.items():
            key_lower = key.lower()
            if not result['name'] and any(nf in key_lower for nf in name_fields):
                result['name'] = str(value).strip()
            elif not result['phone'] and any(pf in key_lower for pf in phone_fields):
                result['phone'] = str(value).strip()
            elif not result['email'] and any(ef in key_lower for ef in email_fields):
                result['email'] = str(value).strip()
    
    return result


@receiver(post_save, sender=BookingSubmission)
def create_lead_from_booking_submission(sender, instance, created, **kwargs):
    """Создать лид при отправке формы записи, если включена интеграция с CRM"""
    if not created:
        return  # Обрабатываем только новые записи
    
    # Проверяем, включена ли интеграция с CRM
    if not instance.form.integrate_with_crm:
        return
    
    # Извлекаем контактные данные из данных формы
    form_data = instance.data or {}
    contact_data = extract_contact_data(form_data)
    
    # Если нет контактных данных, не создаем лид
    if not any([contact_data['name'], contact_data['phone'], contact_data['email']]):
        return
    
    # Получаем или создаем статус "Новый"
    status = LeadStatus.objects.filter(code='new').first()
    if not status:
        status = LeadStatus.objects.create(
            name='Новый',
            code='new',
            color='#28a745',
            order=0
        )
    
    # Создаем лид
    lead = Lead.objects.create(
        booking_submission=instance,
        status=status,
        source=f'Форма записи: {instance.form.title}',
        additional_data=''  # Будет установлено через set_additional_data
    )
    
    # Устанавливаем зашифрованные данные
    if contact_data['name']:
        lead.set_name(contact_data['name'])
    if contact_data['phone']:
        lead.set_phone(contact_data['phone'])
    if contact_data['email']:
        lead.set_email(contact_data['email'])
    
    # Сохраняем дополнительные данные
    additional_data = {k: v for k, v in form_data.items() 
                      if k.lower() not in ['name', 'имя', 'fio', 'фио', 'phone', 'телефон', 'email', 'e-mail']}
    if additional_data:
        lead.set_additional_data(additional_data)
    
    lead.save()
    
    return lead


@receiver(post_save, sender=QuizSubmission)
def create_lead_from_quiz_submission(sender, instance, created, **kwargs):
    """Создать лид при отправке анкеты, если включена интеграция с CRM"""
    if not created:
        return  # Обрабатываем только новые записи
    
    # Проверяем, включена ли интеграция с CRM
    if not instance.quiz.integrate_with_crm:
        return
    
    # Извлекаем контактные данные
    contact_data = {
        'name': instance.user_name or '',
        'phone': instance.user_phone or '',
        'email': instance.user_email or ''
    }
    
    # Если нет контактных данных, не создаем лид
    if not any([contact_data['name'], contact_data['phone'], contact_data['email']]):
        return
    
    # Получаем или создаем статус "Новый"
    status = LeadStatus.objects.filter(code='new').first()
    if not status:
        status = LeadStatus.objects.create(
            name='Новый',
            code='new',
            color='#28a745',
            order=0
        )
    
    # Собираем дополнительные данные из ответов
    additional_data = {
        'quiz_title': instance.quiz.title,
        'total_points': instance.total_points,
        'result_title': instance.result.title if instance.result else None,
    }
    
    # Добавляем ответы на вопросы
    answers_data = {}
    for answer in instance.answers.all():
        answer_text = ''
        if answer.selected_options.exists():
            answer_text = ', '.join([opt.text for opt in answer.selected_options.all()])
        elif answer.text_answer:
            answer_text = answer.text_answer
        
        if answer_text:
            answers_data[answer.question.text[:100]] = answer_text
    
    if answers_data:
        additional_data['answers'] = answers_data
    
    # Создаем лид
    lead = Lead.objects.create(
        quiz_submission=instance,
        status=status,
        source=f'Анкета: {instance.quiz.title}',
        additional_data=''  # Будет установлено через set_additional_data
    )
    
    # Устанавливаем зашифрованные данные
    if contact_data['name']:
        lead.set_name(contact_data['name'])
    if contact_data['phone']:
        lead.set_phone(contact_data['phone'])
    if contact_data['email']:
        lead.set_email(contact_data['email'])
    
    # Сохраняем дополнительные данные
    if additional_data:
        lead.set_additional_data(additional_data)
    
    lead.save()
    
    return lead

