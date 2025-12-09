"""
Сигналы для отправки уведомлений в Telegram
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from .models import TelegramBotSettings
from .bot import send_notification_to_admins
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='quizzes.QuizSubmission')
def notify_quiz_submission(sender, instance, created, **kwargs):
    """Уведомление при прохождении анкеты (асинхронно через threading)"""
    if not created:
        return
    
    # Запускаем отправку уведомления в отдельном потоке
    import threading
    
    def send_notification():
        bot_settings = TelegramBotSettings.objects.first()
        if not bot_settings or not bot_settings.is_active or not bot_settings.notify_on_quiz:
            return
        
        # Формируем текст уведомления
        quiz_title = instance.quiz.title if instance.quiz else 'Неизвестная анкета'
        user_name = instance.user_name or 'Не указано'
        user_phone = instance.user_phone or 'Не указано'
        total_points = instance.total_points
        result_title = instance.result.title if instance.result else 'Не определен'
        
        text = (
            f'📋 <b>Новое прохождение анкеты</b>\n\n'
            f'Анкета: {quiz_title}\n'
            f'Имя: {user_name}\n'
            f'Телефон: {user_phone}\n'
            f'Баллы: {total_points}\n'
            f'Результат: {result_title}\n'
            f'Время: {instance.created_at.strftime("%d.%m.%Y %H:%M")}'
        )
        
        send_notification_to_admins(text)
    
    thread = threading.Thread(target=send_notification, daemon=True)
    thread.start()


@receiver(post_save, sender='booking.BookingSubmission')
def notify_booking_submission(sender, instance, created, **kwargs):
    """Уведомление при новой записи (асинхронно через threading)"""
    if not created:
        return
    
    # Запускаем отправку уведомления в отдельном потоке
    import threading
    
    def send_notification():
        bot_settings = TelegramBotSettings.objects.first()
        if not bot_settings or not bot_settings.is_active or not bot_settings.notify_on_booking:
            return
        
        # Формируем текст уведомления
        form_title = instance.form.title if instance.form else 'Неизвестная форма'
        service_title = instance.service.title if instance.service else 'Не указана'
        
        # Извлекаем данные из формы
        form_data = instance.data or {}
        
        # Логируем для отладки
        logger.info(f'Telegram уведомление: form_data={form_data}')
        
        # Начинаем формировать текст уведомления
        text = (
            f'📝 <b>Новая запись</b>\n\n'
            f'Форма: {form_title}\n'
            f'Услуга: {service_title}\n\n'
        )
        
        # Получаем все поля формы и показываем их значения
        if instance.form:
            # Получаем поля формы, отсортированные по порядку
            form_fields = instance.form.fields.all().order_by('order', 'id')
            
            # Собираем данные по полям формы
            fields_data = []
            for field in form_fields:
                # Пропускаем скрытые поля (если нужно)
                # if field.field_type == 'hidden':
                #     continue
                
                # Получаем значение поля из данных формы
                field_value = form_data.get(field.name, '')
                
                # Если значение пустое, пробуем найти по разным вариантам имени (регистронезависимо)
                if not field_value:
                    for key in form_data.keys():
                        if key.lower() == field.name.lower():
                            field_value = form_data[key]
                            break
                
                # Если значение все еще пустое, показываем "Не указано"
                if not field_value:
                    field_value = 'Не указано'
                
                # Добавляем поле в список
                fields_data.append((field.label, field_value))
            
            # Если есть поля формы, показываем их
            if fields_data:
                text += '<b>Данные формы:</b>\n'
                for label, value in fields_data:
                    # Экранируем HTML символы для безопасности
                    value_str = str(value).replace('<', '&lt;').replace('>', '&gt;')
                    text += f'{label}: {value_str}\n'
            else:
                # Если полей нет, показываем все данные как есть
                text += '<b>Данные формы:</b>\n'
                for key, value in form_data.items():
                    value_str = str(value).replace('<', '&lt;').replace('>', '&gt;')
                    text += f'{key}: {value_str}\n'
        else:
            # Если форма не найдена, показываем все данные как есть
            text += '<b>Данные формы:</b>\n'
            for key, value in form_data.items():
                value_str = str(value).replace('<', '&lt;').replace('>', '&gt;')
                text += f'{key}: {value_str}\n'
        
        text += f'\nВремя: {instance.created_at.strftime("%d.%m.%Y %H:%M")}'
        
        send_notification_to_admins(text)
    
    thread = threading.Thread(target=send_notification, daemon=True)
    thread.start()


def _get_banner_notification_key(banner_id, notification_type):
    """Генерирует ключ для кэша уведомления о баннере"""
    return f'telegram_banner_notification_{banner_id}_{notification_type}'


def _was_notification_sent(banner_id, notification_type):
    """Проверяет, было ли уже отправлено уведомление"""
    key = _get_banner_notification_key(banner_id, notification_type)
    return cache.get(key, False)


def _mark_notification_sent(banner_id, notification_type, timeout=86400):
    """Помечает уведомление как отправленное (таймаут 24 часа)"""
    key = _get_banner_notification_key(banner_id, notification_type)
    cache.set(key, True, timeout)


@receiver(pre_save, sender='content.WelcomeBanner')
def check_banner_on_save(sender, instance, **kwargs):
    """
    Проверяет баннер при сохранении и отправляет уведомления
    """
    bot_settings = TelegramBotSettings.objects.first()
    if not bot_settings or not bot_settings.is_active:
        return
    
    now = timezone.now()
    
    # Проверяем, был ли баннер сохранен ранее
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            old_start_at = old_instance.start_at
            old_end_at = old_instance.end_at
        except sender.DoesNotExist:
            old_start_at = None
            old_end_at = None
    else:
        old_start_at = None
        old_end_at = None
    
    # Проверяем начало отображения
    if (bot_settings.notify_on_banner_start and 
        instance.start_at and 
        instance.is_active):
        # Если время начала изменилось или баннер новый
        if old_start_at != instance.start_at:
            # Проверяем, начал ли баннер отображаться сейчас
            if instance.start_at <= now:
                # Проверяем, не было ли уже отправлено уведомление
                if not _was_notification_sent(instance.pk or 0, 'start'):
                    banner_name = instance.title or (f"Баннер #{instance.pk}" if instance.pk else "новый баннер")
                    text = (
                        f'🎉 <b>Баннер начал отображаться</b>\n\n'
                        f'Название: {banner_name}\n'
                        f'Время начала: {instance.start_at.strftime("%d.%m.%Y %H:%M")}'
                    )
                    if instance.end_at:
                        text += f'\nВремя окончания: {instance.end_at.strftime("%d.%m.%Y %H:%M")}'
                    
                    if send_notification_to_admins(text) > 0 and instance.pk:
                        _mark_notification_sent(instance.pk, 'start')
    
    # Проверяем завершение отображения
    if (bot_settings.notify_on_banner_end and 
        instance.end_at):
        # Если время окончания изменилось
        if old_end_at != instance.end_at:
            # Проверяем, завершил ли баннер отображение сейчас
            if instance.end_at <= now:
                # Проверяем, не было ли уже отправлено уведомление
                if not _was_notification_sent(instance.pk or 0, 'end'):
                    banner_name = instance.title or (f"Баннер #{instance.pk}" if instance.pk else "новый баннер")
                    text = (
                        f'🏁 <b>Баннер завершил отображение</b>\n\n'
                        f'Название: {banner_name}\n'
                        f'Время окончания: {instance.end_at.strftime("%d.%m.%Y %H:%M")}'
                    )
                    
                    if send_notification_to_admins(text) > 0 and instance.pk:
                        _mark_notification_sent(instance.pk, 'end')


def check_banner_notifications():
    """
    Проверяет и отправляет уведомления о начале/завершении отображения баннеров
    Эта функция должна вызываться периодически (например, через cron или celery)
    """
    from content.models import WelcomeBanner
    
    bot_settings = TelegramBotSettings.objects.first()
    if not bot_settings or not bot_settings.is_active:
        return
    
    now = timezone.now()
    
    # Проверяем все активные баннеры
    banners = WelcomeBanner.objects.filter(is_active=True)
    
    for banner in banners:
        # Проверяем начало отображения (в пределах 5 минут)
        if (bot_settings.notify_on_banner_start and 
            banner.start_at and 
            banner.start_at <= now):
            time_diff = (now - banner.start_at).total_seconds()
            # Проверяем, что прошло не более 5 минут с начала
            if 0 <= time_diff <= 300:
                # Проверяем, не было ли уже отправлено уведомление
                if not _was_notification_sent(banner.id, 'start'):
                    text = (
                        f'🎉 <b>Баннер начал отображаться</b>\n\n'
                        f'Название: {banner.title or f"Баннер #{banner.id}"}\n'
                        f'Время начала: {banner.start_at.strftime("%d.%m.%Y %H:%M")}'
                    )
                    if banner.end_at:
                        text += f'\nВремя окончания: {banner.end_at.strftime("%d.%m.%Y %H:%M")}'
                    
                    if send_notification_to_admins(text) > 0:
                        _mark_notification_sent(banner.id, 'start')
        
        # Проверяем завершение отображения (в пределах 5 минут)
        if (bot_settings.notify_on_banner_end and 
            banner.end_at and 
            banner.end_at <= now):
            time_diff = (now - banner.end_at).total_seconds()
            # Проверяем, что прошло не более 5 минут с окончания
            if 0 <= time_diff <= 300:
                # Проверяем, не было ли уже отправлено уведомление
                if not _was_notification_sent(banner.id, 'end'):
                    text = (
                        f'🏁 <b>Баннер завершил отображение</b>\n\n'
                        f'Название: {banner.title or f"Баннер #{banner.id}"}\n'
                        f'Время окончания: {banner.end_at.strftime("%d.%m.%Y %H:%M")}'
                    )
                    
                    if send_notification_to_admins(text) > 0:
                        _mark_notification_sent(banner.id, 'end')

