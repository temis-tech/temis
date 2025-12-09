"""
Асинхронные задачи для обработки отправок форм
"""
import threading
import logging
from .models import BookingSubmission
from moyklass.models import MoyKlassSettings, MoyKlassIntegration
from moyklass.client import MoyKlassClient, MoyKlassAPIError
from telegram.models import TelegramBotSettings
from telegram.bot import send_notification_to_admins

logger = logging.getLogger(__name__)


def process_booking_submission_async(submission_id):
    """
    Асинхронная обработка отправки формы записи
    Запускается в отдельном потоке
    """
    try:
        submission = BookingSubmission.objects.get(id=submission_id)
    except BookingSubmission.DoesNotExist:
        logger.error(f'BookingSubmission {submission_id} не найдена')
        return
    
    # Обработка интеграции с MoyKlass
    process_moyklass_integration(submission)
    
    # Отправка уведомления в Telegram
    # (уведомление уже отправляется через сигнал, но можно оставить здесь для контроля)


def process_moyklass_integration(submission):
    """Обработка интеграции с MoyKlass"""
    # Проверяем, активна ли интеграция
    settings = MoyKlassSettings.objects.first()
    if not settings or not settings.is_active:
        return
    
    # Ищем активную интеграцию для этой формы
    if not submission.form:
        return
    
    integration = MoyKlassIntegration.objects.filter(
        booking_form=submission.form,
        is_active=True
    ).first()
    
    if not integration:
        logger.debug(f'Интеграция не найдена для формы {submission.form.id}')
        return
    
    try:
        client = MoyKlassClient(settings)
        
        # Извлекаем данные из формы
        form_data = submission.data or {}
        
        # Используем маппинг полей для формирования данных
        student_data = {}
        comment_parts = []
        
        # Логируем все данные формы для отладки
        logger.info(f'Обработка MoyKlass интеграции для формы {submission.form.id}. Данные: {form_data}')
        
        # Обрабатываем маппинги полей
        for mapping in integration.field_mappings.all().order_by('order'):
            # Пробуем получить значение по имени поля (с учетом регистра)
            source_value = form_data.get(mapping.source_field_name, '')
            
            # Если не найдено, пробуем найти по разным вариантам имени (регистронезависимо)
            if not source_value:
                for key in form_data.keys():
                    if key.lower() == mapping.source_field_name.lower():
                        source_value = form_data[key]
                        break
            
            # Если значение пустое и есть значение по умолчанию
            if not source_value and mapping.default_value:
                source_value = mapping.default_value
            
            # Логируем маппинг для отладки
            logger.debug(
                f'Маппинг поля: {mapping.source_field_name} -> {mapping.moyklass_field}, '
                f'Значение: "{source_value}", Обязательное: {mapping.is_required}'
            )
            
            # Если поле обязательное и пустое - пропускаем создание лида
            if mapping.is_required and not source_value:
                logger.warning(
                    f'Обязательное поле {mapping.moyklass_field} не заполнено для формы {submission.form.id}. '
                    f'Поле: {mapping.source_field_name}, Данные формы: {form_data}'
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
        if submission.service:
            comment_parts.insert(0, f'Услуга: {submission.service.title}')
        if submission.form:
            comment_parts.insert(0, f'Форма: {submission.form.title}')
        
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
            f'Создан лид в MoyKlass: ID={moyklass_student_id}, '
            f'Имя={student_data.get("name", "Не указано")}, '
            f'Телефон={student_data.get("phone", "Не указано")}'
        )
        
    except MoyKlassAPIError as e:
        logger.error(f'Ошибка создания лида в MoyKlass: {str(e)}')
    except Exception as e:
        logger.error(f'Неожиданная ошибка при создании лида в MoyKlass: {str(e)}')


def process_quiz_submission_async(submission_id):
    """
    Асинхронная обработка отправки анкеты
    Запускается в отдельном потоке
    """
    try:
        from quizzes.models import QuizSubmission
        submission = QuizSubmission.objects.get(id=submission_id)
    except QuizSubmission.DoesNotExist:
        logger.error(f'QuizSubmission {submission_id} не найдена')
        return
    
    # Обработка интеграции с MoyKlass для анкет
    # (если нужно, можно добавить аналогичную логику)

