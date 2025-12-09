"""
Сигналы для автоматической интеграции с MoyKlass для анкет
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QuizSubmission
from moyklass.models import MoyKlassSettings, MoyKlassIntegration
from moyklass.client import MoyKlassClient, MoyKlassAPIError
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=QuizSubmission)
def create_moyklass_student_from_quiz(sender, instance, created, **kwargs):
    """
    Автоматически создает лида в MoyKlass при создании новой отправки анкеты
    Использует настройки маппинга полей из MoyKlassIntegration
    """
    if not created:
        return  # Обрабатываем только новые записи
    
    # Проверяем, активна ли интеграция
    settings = MoyKlassSettings.objects.first()
    if not settings or not settings.is_active:
        return
    
    # Ищем активную интеграцию для этой анкеты
    if not instance.quiz:
        return
    
    integration = MoyKlassIntegration.objects.filter(
        quiz=instance.quiz,
        is_active=True
    ).first()
    
    if not integration:
        logger.debug(f'Интеграция не найдена для анкеты {instance.quiz.id}')
        return
    
    try:
        client = MoyKlassClient(settings)
        
        # Формируем данные из ответов анкеты
        quiz_data = {}
        
        # Добавляем базовые данные пользователя
        if instance.user_name:
            quiz_data['user_name'] = instance.user_name
        if instance.user_phone:
            quiz_data['user_phone'] = instance.user_phone
        if instance.user_email:
            quiz_data['user_email'] = instance.user_email
        
        # Добавляем данные из ответов
        for answer in instance.answers.all():
            question_id = str(answer.question.id)
            if answer.text_answer:
                quiz_data[f'question_{question_id}'] = answer.text_answer
            elif answer.selected_options.exists():
                selected_texts = [opt.text for opt in answer.selected_options.all()]
                quiz_data[f'question_{question_id}'] = ', '.join(selected_texts)
        
        # Используем маппинг полей для формирования данных
        student_data = {}
        comment_parts = []
        
        # Обрабатываем маппинги полей
        for mapping in integration.field_mappings.all().order_by('order'):
            # Получаем значение из данных анкеты
            source_value = quiz_data.get(mapping.source_field_name, '')
            
            # Если значение пустое и есть значение по умолчанию
            if not source_value and mapping.default_value:
                source_value = mapping.default_value
            
            # Если поле обязательное и пустое - пропускаем создание лида
            if mapping.is_required and not source_value:
                logger.warning(
                    f'Обязательное поле {mapping.moyklass_field} не заполнено для анкеты {instance.quiz.id}'
                )
                return
            
            # Добавляем значение в соответствующие поля
            if mapping.moyklass_field == 'comment':
                if source_value:
                    comment_parts.append(f'{mapping.source_field_label or mapping.source_field_name}: {source_value}')
            elif mapping.moyklass_field == 'phone':
                # Нормализуем телефон: оставляем только цифры (MoyKlass требует ^[0-9]{10,15}$)
                phone_str = str(source_value).strip()
                phone_digits = ''.join(filter(str.isdigit, phone_str))
                
                # Логируем для отладки
                logger.debug(
                    f'Нормализация телефона: исходное="{phone_str}", '
                    f'после нормализации="{phone_digits}", длина={len(phone_digits)}'
                )
                
                # Проверяем длину (MoyKlass требует 10-15 цифр)
                if phone_digits:
                    if len(phone_digits) < 10:
                        logger.warning(
                            f'Телефон слишком короткий: "{phone_digits}" (длина {len(phone_digits)}, требуется 10-15)'
                        )
                    elif len(phone_digits) > 15:
                        logger.warning(
                            f'Телефон слишком длинный: "{phone_digits}" (длина {len(phone_digits)}, требуется 10-15), обрезаем до 15'
                        )
                        phone_digits = phone_digits[:15]
                    
                    student_data[mapping.moyklass_field] = phone_digits
                else:
                    logger.warning(f'Не удалось нормализовать телефон из значения: "{source_value}"')
            else:
                student_data[mapping.moyklass_field] = source_value
        
        # Добавляем дополнительную информацию в комментарий
        if instance.quiz:
            comment_parts.insert(0, f'Анкета: {instance.quiz.title}')
        if instance.total_points:
            comment_parts.insert(1, f'Баллы: {instance.total_points}')
        if instance.result:
            comment_parts.insert(2, f'Результат: {instance.result.title}')
        
        if comment_parts:
            student_data['comment'] = '\n'.join(comment_parts)
        
        # Добавляем тег из настроек
        tags = []
        if settings.website_tag_name:
            tags = [settings.website_tag_name]
        
        # Создаем лида в MoyKlass
        result = client.create_student(student_data, tags=tags)
        moyklass_student_id = result.get('id')
        
        logger.info(
            f'Создан лид в MoyKlass из анкеты: ID={moyklass_student_id}, '
            f'Имя={student_data.get("name", "Не указано")}, '
            f'Телефон={student_data.get("phone", "Не указано")}'
        )
        
    except MoyKlassAPIError as e:
        logger.error(f'Ошибка создания лида в MoyKlass: {str(e)}')
    except Exception as e:
        logger.error(f'Неожиданная ошибка при создании лида в MoyKlass: {str(e)}')

