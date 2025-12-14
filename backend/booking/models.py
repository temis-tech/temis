from django.db import models
from django.core.validators import MinValueValidator
from content.models import Service
from quizzes.models import Quiz


class BookingForm(models.Model):
    """Форма записи на услугу"""
    title = models.CharField('Название формы', max_length=200)
    description = models.TextField('Описание', blank=True)
    submit_button_text = models.CharField('Текст кнопки отправки', max_length=100, default='Записаться')
    success_message = models.TextField('Сообщение об успешной отправке', 
                                       default='Спасибо! Мы свяжемся с вами в ближайшее время.')
    default_quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Анкета по умолчанию',
                                   help_text='Анкета, которая откроется всегда при отправке формы (без условий). Если указана, будет показана вместо отправки формы.')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Форма записи'
        verbose_name_plural = 'Формы записи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FormField(models.Model):
    """Поле формы записи"""
    FIELD_TYPES = [
        ('text', 'Текст'),
        ('email', 'Email'),
        ('phone', 'Телефон'),
        ('textarea', 'Многострочный текст'),
        ('select', 'Выпадающий список'),
        ('radio', 'Радиокнопки'),
        ('checkbox', 'Чекбокс'),
        ('date', 'Дата'),
        ('time', 'Время'),
        ('hidden', 'Скрытое поле'),
    ]
    
    form = models.ForeignKey(BookingForm, on_delete=models.CASCADE, related_name='fields', verbose_name='Форма')
    label = models.CharField('Название поля', max_length=200)
    field_type = models.CharField('Тип поля', max_length=20, choices=FIELD_TYPES, default='text')
    name = models.CharField('Имя поля (name)', max_length=100, 
                           help_text='Используется в HTML, должно быть уникальным в форме')
    placeholder = models.CharField('Подсказка', max_length=200, blank=True)
    help_text = models.CharField('Дополнительная подсказка', max_length=500, blank=True)
    is_required = models.BooleanField('Обязательное', default=True)
    order = models.IntegerField('Порядок', default=0)
    default_value = models.CharField('Значение по умолчанию', max_length=500, blank=True,
                                    help_text='Для скрытых полей можно использовать {service_title} для подстановки названия услуги')
    options = models.TextField('Варианты выбора (для select/radio)', blank=True,
                               help_text='Каждый вариант с новой строки')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Поле формы'
        verbose_name_plural = 'Поля формы'
        ordering = ['order', 'id']
        unique_together = [['form', 'name']]

    def __str__(self):
        return f'{self.form.title} - {self.label}'


class FormRule(models.Model):
    """Правило для формы: при определенном значении поля открыть анкету"""
    form = models.ForeignKey(BookingForm, on_delete=models.CASCADE, related_name='rules', verbose_name='Форма')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, verbose_name='Поле')
    field_value = models.CharField('Значение поля', max_length=500,
                                   help_text='Если поле имеет это значение, сработает правило')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True, 
                            verbose_name='Анкета',
                            help_text='Анкета, которая откроется при срабатывании правила')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Правило формы'
        verbose_name_plural = 'Правила формы'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.form.title} - {self.field.label} = {self.field_value}'


class BookingSubmission(models.Model):
    """Отправка формы записи"""
    form = models.ForeignKey(BookingForm, on_delete=models.CASCADE, related_name='submissions', verbose_name='Форма')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, 
                               verbose_name='Услуга', related_name='bookings')
    data = models.JSONField('Данные формы', default=dict, 
                           help_text='Все данные, отправленные через форму')
    source_page = models.CharField('Страница источника', max_length=500, blank=True,
                                   help_text='URL страницы, с которой была отправлена форма')
    quiz_submission = models.ForeignKey('quizzes.QuizSubmission', on_delete=models.SET_NULL, 
                                       null=True, blank=True, verbose_name='Отправка анкеты',
                                       related_name='booking_submissions')
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Отправка формы записи'
        verbose_name_plural = 'Отправки форм записи'
        ordering = ['-created_at']

    def __str__(self):
        service_name = self.service.title if self.service else 'Без услуги'
        return f'{self.form.title} - {service_name} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'

