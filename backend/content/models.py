from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from .utils.image_processing import process_uploaded_image
import re

User = get_user_model()


def transliterate_slug(text):
    """Транслитерация кириллицы в латиницу для slug"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    text = text.lower()
    slug = ''.join(translit_map.get(c, c) for c in text)
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')[:50]


class Branch(models.Model):
    """Филиалы центра"""
    name = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=300)
    metro = models.CharField('Метро', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    image = models.ImageField('Изображение', upload_to='branches/', blank=True, null=True)
    # Связь со страницей контента - позволяет создать страницу филиала через конструктор
    content_page = models.ForeignKey('ContentPage', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='branches', verbose_name='Страница филиала',
                                    help_text='Страница контента для отображения информации о филиале через конструктор')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'
        ordering = ['order', 'name']
        app_label = 'content'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Сохраняем сначала, чтобы получить путь к файлу
        super().save(*args, **kwargs)
        # Обрабатываем изображение после сохранения
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                # Сохраняем еще раз после обработки
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для Branch {self.name}: {e}")


class Service(models.Model):
    """Услуги центра"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True)
    description = RichTextField('Описание', blank=True,
                               help_text='Описание услуги с поддержкой форматирования текста')
    short_description = models.TextField('Краткое описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_is_from = models.BooleanField('Цена "От"', default=False,
                                       help_text='Если включено, перед ценой будет отображаться "От" (например, "От 1000 ₽")')
    price_with_abonement = models.DecimalField('Цена по абонементу', max_digits=10, decimal_places=2, 
                                                validators=[MinValueValidator(0)], blank=True, null=True)
    price_with_abonement_is_from = models.BooleanField('Цена по абонементу "От"', default=False,
                                                        help_text='Если включено, перед ценой по абонементу будет отображаться "От"')
    duration = models.CharField('Длительность', max_length=50, default='45 минут')
    image = models.ImageField('Изображение', upload_to='services/', blank=True, null=True)
    
    # Настройки изображения
    IMAGE_ALIGN_CHOICES = [
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('center', 'По центру'),
        ('full', 'На всю ширину'),
    ]
    
    IMAGE_SIZE_CHOICES = [
        ('small', 'Маленькое (200px)'),
        ('medium', 'Среднее (400px)'),
        ('large', 'Большое (600px)'),
        ('full', 'На всю ширину'),
    ]
    
    image_align = models.CharField('Выравнивание изображения', max_length=10, choices=IMAGE_ALIGN_CHOICES, default='center',
                                   help_text='Как изображение выравнивается относительно текста')
    image_size = models.CharField('Размер изображения', max_length=10, choices=IMAGE_SIZE_CHOICES, default='medium',
                                 help_text='Размер изображения')
    
    # Расположение блоков с ценой и длительностью
    PRICE_DURATION_POSITION_CHOICES = [
        ('top', 'Сверху текста'),
        ('bottom', 'Снизу текста'),
        ('hidden', 'Не отображать'),
    ]
    price_duration_position = models.CharField('Расположение блоков цены и длительности', 
                                               max_length=10, 
                                               choices=PRICE_DURATION_POSITION_CHOICES, 
                                               default='top',
                                               help_text='Где отображать блоки с ценой и длительностью относительно описания')
    
    has_own_page = models.BooleanField('Может быть открыта как страница', default=False,
                                      help_text='Если включено, услуга будет иметь свой URL и может быть открыта как отдельная страница')
    show_booking_button = models.BooleanField('Показывать кнопку "Записаться"', default=True,
                                             help_text='Отображать кнопку записи на карточке и странице услуги')
    booking_form = models.ForeignKey('booking.BookingForm', on_delete=models.SET_NULL, 
                                     null=True, blank=True, verbose_name='Форма записи',
                                     help_text='Форма, которая откроется при нажатии на кнопку "Записаться"')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'title']
        app_label = 'content'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Возвращает URL страницы услуги"""
        if self.has_own_page and self.slug:
            return f'/services/{self.slug}/'
        return None
    
    def save(self, *args, **kwargs):
        if not self.slug and self.has_own_page:
            self.slug = transliterate_slug(self.title) or f'service-{self.id or 0}'
        
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем изображение после сохранения
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для Service {self.title}: {e}")


class Specialist(models.Model):
    """Логопеды/специалисты"""
    name = models.CharField('Имя', max_length=200)
    position = models.CharField('Должность', max_length=200)
    bio = models.TextField('Биография', blank=True)
    photo = models.ImageField('Фото', upload_to='specialists/', blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, 
                              verbose_name='Филиал', related_name='specialists')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'
        ordering = ['order', 'name']
        app_label = 'content'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем фото после сохранения
        if self.photo and hasattr(self.photo, 'file'):
            try:
                process_uploaded_image(self.photo, image_type='avatar')
                super().save(update_fields=['photo'])
            except Exception as e:
                print(f"Ошибка обработки фото для Specialist {self.name}: {e}")


class ServiceBranch(models.Model):
    """Связь услуги с филиалом - позволяет настроить индивидуальные цены и настройки"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_branches',
                               verbose_name='Услуга')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='Филиал',
                              help_text='Если филиал удален, связь сохраняется для истории')
    
    # Цены (если null - используются базовые из Service)
    price = models.DecimalField('Цена в этом филиале', max_digits=10, decimal_places=2, null=True, blank=True,
                               help_text='Если не указана, используется базовая цена из услуги')
    price_with_abonement = models.DecimalField('Цена по абонементу', max_digits=10, decimal_places=2, null=True, blank=True,
                                              help_text='Если не указана, используется базовая цена по абонементу из услуги')
    
    # Доступность и порядок
    is_available = models.BooleanField('Доступна в этом филиале', default=True,
                                      help_text='Можно временно отключить услугу в конкретном филиале')
    order = models.IntegerField('Порядок отображения', default=0,
                               help_text='Порядок отображения услуги в списке услуг филиала')
    
    # Интеграция с CRM МойКласс
    crm_item_id = models.CharField('ID айтема в CRM МойКласс', max_length=100, blank=True, null=True,
                                  help_text='ID услуги/айтема в системе МойКласс для синхронизации данных')
    crm_item_data = models.JSONField('Данные из CRM', blank=True, null=True,
                                     help_text='Дополнительные данные из CRM (цены абонементов, условия и т.д.)')
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Услуга в филиале'
        verbose_name_plural = 'Услуги в филиалах'
        unique_together = [['service', 'branch']]  # Одна услуга - один раз в филиале
        ordering = ['order', 'branch__order', 'service__order']
        indexes = [
            models.Index(fields=['service', 'branch']),
            models.Index(fields=['is_available', 'branch']),
        ]
    
    def __str__(self):
        branch_name = self.branch.name if self.branch else 'Удаленный филиал'
        return f'{self.service.title} - {branch_name}'
    
    def save(self, *args, **kwargs):
        # Сохраняем текущие цены в историю перед обновлением
        user = kwargs.pop('changed_by', None)
        if self.pk:  # Только для существующих записей
            try:
                old_instance = ServiceBranch.objects.get(pk=self.pk)
                price_changed = old_instance.price != self.price
                abonement_price_changed = old_instance.price_with_abonement != self.price_with_abonement
                
                if price_changed or abonement_price_changed:
                    # Определяем финальные цены для истории
                    final_price = self.price if self.price is not None else self.service.price
                    final_abonement_price = self.price_with_abonement if self.price_with_abonement is not None else self.service.price_with_abonement
                    
                    ServiceBranchPriceHistory.objects.create(
                        service_branch=self,
                        price=final_price,
                        price_with_abonement=final_abonement_price,
                        changed_by=user
                    )
            except ServiceBranch.DoesNotExist:
                pass  # Новая запись, истории нет
        super().save(*args, **kwargs)
    
    def get_final_price(self):
        """Возвращает финальную цену: из ServiceBranch или из Service"""
        return self.price if self.price is not None else self.service.price
    
    def get_final_price_with_abonement(self):
        """Возвращает финальную цену по абонементу: из ServiceBranch или из Service"""
        return self.price_with_abonement if self.price_with_abonement is not None else self.service.price_with_abonement


class ServiceBranchPriceHistory(models.Model):
    """История изменений цен услуг в филиалах (аудит)"""
    service_branch = models.ForeignKey(ServiceBranch, on_delete=models.CASCADE, related_name='price_history',
                                      verbose_name='Услуга в филиале')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    price_with_abonement = models.DecimalField('Цена по абонементу', max_digits=10, decimal_places=2, null=True, blank=True)
    changed_at = models.DateTimeField('Изменено', auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Изменено пользователем')
    notes = models.TextField('Примечание', blank=True,
                            help_text='Причина изменения цены или дополнительная информация')
    
    class Meta:
        verbose_name = 'История изменения цены'
        verbose_name_plural = 'История изменений цен'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['service_branch', '-changed_at']),
        ]
    
    def __str__(self):
        return f'{self.service_branch} - {self.changed_at.strftime("%d.%m.%Y %H:%M")}'


class Review(models.Model):
    """Отзывы"""
    author_name = models.CharField('Имя автора', max_length=200)
    author_photo = models.ImageField('Фото автора', upload_to='reviews/', blank=True, null=True)
    text = models.TextField('Текст отзыва')
    rating = models.IntegerField('Рейтинг', default=5, validators=[MinValueValidator(1), 
                                                                    MaxValueValidator(5)])
    is_published = models.BooleanField('Опубликован', default=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-order', '-created_at']
        app_label = 'content'

    def __str__(self):
        return f'{self.author_name} - {self.rating}⭐'
    
    def save(self, *args, **kwargs):
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем фото автора после сохранения
        if self.author_photo and hasattr(self.author_photo, 'file'):
            try:
                process_uploaded_image(self.author_photo, image_type='avatar')
                super().save(update_fields=['author_photo'])
            except Exception as e:
                print(f"Ошибка обработки фото для Review {self.author_name}: {e}")


class Promotion(models.Model):
    """Акции"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True)
    description = models.TextField('Описание')
    image = models.ImageField('Изображение', upload_to='promotions/', blank=True, null=True)
    start_date = models.DateField('Дата начала', blank=True, null=True)
    end_date = models.DateField('Дата окончания', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-order', '-created_at']
        app_label = 'content'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_slug(self.title) or f'promotion-{self.id or 0}'
        
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем изображение после сохранения
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для Promotion {self.title}: {e}")


class Article(models.Model):
    """Статьи"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True)
    content = models.TextField('Содержание')
    short_description = models.TextField('Краткое описание', blank=True)
    image = models.ImageField('Изображение', upload_to='articles/', blank=True, null=True)
    is_published = models.BooleanField('Опубликована', default=True)
    views_count = models.IntegerField('Просмотры', default=0)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']
        app_label = 'content'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_slug(self.title) or f'article-{self.id or 0}'
        
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем изображение после сохранения
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для Article {self.title}: {e}")


class Contact(models.Model):
    """Контактная информация"""
    phone = models.CharField('Телефон', max_length=20)
    phone_secondary = models.CharField('Дополнительный телефон', max_length=20, blank=True)
    inn = models.CharField('ИНН', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return self.phone


class ContentPage(models.Model):
    """Страница контента - основа конструктора"""
    PAGE_TYPES = [
        ('catalog', 'Каталог'),
        ('gallery', 'Галерея'),
        ('home', 'Главная'),
        ('text', 'Описание'),
        ('faq', 'FAQ (Вопросы-Ответы)'),
    ]
    
    title = models.CharField('Название страницы', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True, 
                           help_text='Автоматически генерируется из названия, если не указан')
    page_type = models.CharField('Тип страницы', max_length=20, choices=PAGE_TYPES, default='catalog')
    description = RichTextField('Описание', blank=True, 
                                  help_text='Описание страницы с поддержкой форматирования')
    image = models.ImageField('Изображение', upload_to='content/', blank=True, null=True,
                             help_text='Главное изображение страницы (используется для типа "Описание")')
    
    # Настройки изображения (для типа "Описание")
    IMAGE_ALIGN_CHOICES = [
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('center', 'По центру'),
        ('full', 'На всю ширину'),
    ]
    
    IMAGE_SIZE_CHOICES = [
        ('small', 'Маленькое (200px)'),
        ('medium', 'Среднее (400px)'),
        ('large', 'Большое (600px)'),
        ('full', 'На всю ширину'),
    ]
    
    image_align = models.CharField('Выравнивание изображения', max_length=10, choices=IMAGE_ALIGN_CHOICES, default='center',
                                   help_text='Как изображение выравнивается относительно текста (для типа "Описание")')
    image_size = models.CharField('Размер изображения', max_length=10, choices=IMAGE_SIZE_CHOICES, default='medium',
                                 help_text='Размер изображения (для типа "Описание")')
    
    # Настройки галереи (для типа "Галерея")
    GALLERY_DISPLAY_CHOICES = [
        ('grid', 'Плитка (сетка)'),
        ('carousel', 'Карусель'),
        ('masonry', 'Кирпичная кладка'),
    ]
    
    gallery_display_type = models.CharField('Вид отображения галереи', max_length=20, choices=GALLERY_DISPLAY_CHOICES, default='grid',
                                           help_text='Выберите способ отображения изображений галереи (только для типа "Галерея")')
    gallery_enable_fullscreen = models.BooleanField('Открывать изображения на весь экран', default=True,
                                                    help_text='Если включено, при клике на изображение оно откроется в полноэкранном режиме с возможностью перелистывания (только для типа "Галерея")')
    
    # Настройки FAQ (для типа "FAQ")
    faq_icon = models.ImageField('Иконка вопроса', upload_to='faq/', blank=True, null=True,
                                help_text='Маленькая пиктограммка для вопроса (только для типа "FAQ")')
    faq_icon_position = models.CharField('Позиция иконки', max_length=10, 
                                        choices=[('left', 'Слева'), ('right', 'Справа')], 
                                        default='left',
                                        help_text='Расположение иконки относительно вопроса (только для типа "FAQ")')
    faq_background_color = models.CharField('Цвет фона', max_length=7, default='#FFFFFF', blank=True,
                                          help_text='Цвет фона секции FAQ в формате HEX (например, #FFFFFF) (только для типа "FAQ")')
    faq_background_image = models.ImageField('Фоновое изображение', upload_to='faq/', blank=True, null=True,
                                           help_text='Фоновое изображение для секции FAQ (только для типа "FAQ")')
    faq_animation = models.CharField('Анимация разворачивания', max_length=20,
                                    choices=[('slide', 'Слайд'), ('fade', 'Плавное появление'), ('none', 'Без анимации')],
                                    default='slide',
                                    help_text='Тип анимации при раскрытии вопроса (только для типа "FAQ")')
    faq_columns = models.IntegerField('Количество колонок', default=1,
                                     validators=[MinValueValidator(1), MaxValueValidator(3)],
                                     help_text='Количество вопросов в одной строке (1, 2 или 3). Вопросы будут пропорционально распределены по ширине (только для типа "FAQ")')
    
    show_title = models.BooleanField('Показывать заголовок на странице', default=True,
                                     help_text='Если отключено, заголовок страницы не будет отображаться на сайте')
    
    # Настройки рубрикатора (для типа "Каталог")
    show_catalog_navigator = models.BooleanField('Показывать рубрикатор (навигационный список)', default=False,
                                                  help_text='Если включено, на странице каталога будет отображаться навигационный список элементов каталога для удобной навигации по статьям')
    
    # Выбор каталога или галереи для отображения (для типа "Описание")
    selected_catalog_page = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name='used_as_catalog_in',
                                              verbose_name='Каталог для отображения',
                                              help_text='Выберите страницу с типом "Каталог", которая будет отображаться на этой странице (только для типа "Описание")',
                                              limit_choices_to={'page_type': 'catalog', 'is_active': True})
    selected_gallery_page = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='used_as_gallery_in',
                                             verbose_name='Галерея для отображения',
                                             help_text='Выберите страницу с типом "Галерея", которая будет отображаться на этой странице (только для типа "Описание")',
                                             limit_choices_to={'page_type': 'gallery', 'is_active': True})
    
    # Филиалы для отображения на странице
    display_branches = models.ManyToManyField('Branch', blank=True, 
                                              related_name='displayed_on_pages',
                                              verbose_name='Филиалы для отображения',
                                              help_text='Выберите филиалы, которые будут отображаться на этой странице. Можно использовать для создания страницы контактов или страницы с информацией о филиалах.')
    
    display_services = models.ManyToManyField('Service', blank=True,
                                             related_name='displayed_on_pages',
                                             verbose_name='Услуги для отображения',
                                             help_text='Выберите услуги, которые будут отображаться на этой странице. Услуги будут автоматически фильтроваться по выбранному филиалу, если он указан.')
    
    is_active = models.BooleanField('Активна', default=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Страница контента'
        verbose_name_plural = 'Страницы контента'
        ordering = ['order', 'title']
    
    def __str__(self):
        return f'{self.get_page_type_display()}: {self.title}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_slug(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/{self.slug}/'


class CatalogItem(models.Model):
    """Элемент каталога"""
    BUTTON_TYPES = [
        ('booking', 'Запись'),
        ('quiz', 'Анкета'),
        ('external', 'Внешняя ссылка'),
        ('none', 'Без кнопки'),
    ]
    
    WIDTH_CHOICES = [
        ('narrow', 'Узкая (1/3 ширины)'),
        ('medium', 'Средняя (1/2 ширины)'),
        ('wide', 'Широкая (2/3 ширины)'),
        ('full', 'На всю ширину'),
    ]
    
    page = models.ForeignKey(ContentPage, on_delete=models.CASCADE, related_name='catalog_items',
                            verbose_name='Страница', help_text='Каталог можно добавить на страницу любого типа')
    
    # Связи с услугами и филиалами - позволяет отображать их в каталоге
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='catalog_items', verbose_name='Услуга',
                               help_text='Если выбрана услуга, элемент каталога будет использовать данные услуги (название, описание, изображение, цены)')
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='catalog_items', verbose_name='Филиал',
                              help_text='Если выбран филиал, элемент каталога будет использовать данные филиала (название, адрес, изображение)')
    
    title = models.CharField('Название', max_length=200, blank=True,
                            help_text='Автоматически заполняется из услуги или филиала, если они выбраны. Можно переопределить вручную.')
    slug = models.SlugField('URL', unique=True, blank=True,
                           help_text='Автоматически генерируется из названия, если не указан. Используется для создания страницы элемента.')
    
    # Описание для превью карточки
    card_description = RichTextField('Описание для карточки (превью)', blank=True,
                                     help_text='Краткое описание, которое будет отображаться в карточке элемента в списке каталога. Поддерживает форматирование текста.')
    
    # Описание для страницы элемента
    description = RichTextField('Описание для страницы', blank=True,
                                help_text='Полное описание, которое будет отображаться на странице элемента (если включен режим "Может быть открыт как страница").')
    
    # Изображение для карточки (превью в списке)
    card_image = models.ImageField('Изображение для карточки', upload_to='catalog/cards/', blank=True, null=True,
                                   help_text='Изображение, которое будет отображаться в карточке элемента в списке каталога')
    
    # Изображение для страницы
    image = models.ImageField('Изображение для страницы', upload_to='catalog/', blank=True, null=True,
                             help_text='Изображение, которое будет отображаться на странице элемента (если включен режим "Может быть открыт как страница")')
    
    # Галерея для страницы
    gallery_page = models.ForeignKey(ContentPage, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='catalog_items_with_gallery',
                                    verbose_name='Страница галереи',
                                    help_text='Выберите страницу с типом "Галерея", которая будет отображаться на странице элемента каталога',
                                    limit_choices_to={'page_type': 'gallery'})
    
    # Видео для страницы
    video_url = models.URLField('URL видео', blank=True, null=True,
                               help_text='Ссылка на видео с YouTube, Rutube или другого видеохостинга. Видео будет отображаться на странице элемента с кнопками управления.')
    video_width = models.IntegerField('Ширина видео (px)', blank=True, null=True, default=800,
                                      help_text='Ширина видео-фрейма в пикселях. По умолчанию: 800px')
    video_height = models.IntegerField('Высота видео (px)', blank=True, null=True, default=450,
                                     help_text='Высота видео-фрейма в пикселях. По умолчанию: 450px (соответствует соотношению 16:9 для ширины 800px)')
    
    # Настройки изображения
    IMAGE_ALIGN_CHOICES = [
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('center', 'По центру'),
        ('full', 'На всю ширину'),
    ]
    
    IMAGE_SIZE_CHOICES = [
        ('small', 'Маленькое (200px)'),
        ('medium', 'Среднее (400px)'),
        ('large', 'Большое (600px)'),
        ('full', 'На всю ширину'),
    ]
    
    image_align = models.CharField('Выравнивание изображения', max_length=10, choices=IMAGE_ALIGN_CHOICES, default='center',
                                   help_text='Как изображение выравнивается относительно текста (используется для карточек в списке)')
    image_size = models.CharField('Размер изображения', max_length=10, choices=IMAGE_SIZE_CHOICES, default='medium',
                                 help_text='Размер изображения (используется для карточек в списке)')
    
    # Настройки изображения на странице элемента
    IMAGE_POSITION_CHOICES = [
        ('top', 'Сверху'),
        ('bottom', 'Снизу'),
        ('left', 'Слева'),
        ('right', 'Справа'),
        ('none', 'Не отображать'),
    ]
    
    image_position = models.CharField('Позиция изображения на странице', max_length=10, choices=IMAGE_POSITION_CHOICES, default='top',
                                     help_text='Где отображать изображение на странице элемента: сверху, снизу, слева, справа или не отображать')
    image_target_width = models.IntegerField('Целевая ширина изображения (px)', null=True, blank=True,
                                             help_text='Ширина, к которой будет приведено изображение. Изображение будет вписано в этот размер с сохранением пропорций, центрировано. Если не указано, используется размер по умолчанию.')
    image_target_height = models.IntegerField('Целевая высота изображения (px)', null=True, blank=True,
                                              help_text='Высота, к которой будет приведено изображение. Изображение будет вписано в этот размер с сохранением пропорций, центрировано. Если не указано, используется размер по умолчанию.')
    
    has_own_page = models.BooleanField('Может быть открыт как страница', default=False,
                                      help_text='Если включено, карточка будет иметь свой URL и может быть открыта как отдельная страница')
    width = models.CharField('Ширина элемента', max_length=10, choices=WIDTH_CHOICES, default='medium',
                            help_text='Ширина элемента в сетке каталога')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    
    # Связь с Telegram постом
    telegram_message_id = models.BigIntegerField('ID сообщения Telegram', null=True, blank=True, unique=True,
                                                help_text='ID сообщения из Telegram канала для связи с постом и обновления при редактировании')
    
    # Настройки кнопки
    button_type = models.CharField('Тип кнопки', max_length=20, choices=BUTTON_TYPES, default='none')
    button_text = models.CharField('Текст кнопки', max_length=100, blank=True, default='Записаться')
    button_booking_form = models.ForeignKey('booking.BookingForm', on_delete=models.SET_NULL, null=True, blank=True,
                                            verbose_name='Форма записи',
                                            help_text='Выберите форму записи (если тип кнопки - "Запись")',
                                            limit_choices_to={'is_active': True})
    button_quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Анкета',
                                     help_text='Выберите анкету (если тип кнопки - "Анкета")',
                                     limit_choices_to={'is_active': True})
    button_url = models.CharField('URL кнопки', max_length=500, blank=True,
                                  help_text='Внешняя ссылка (если тип кнопки - "Внешняя ссылка")')
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Элемент каталога'
        verbose_name_plural = 'Элементы каталога'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Возвращает URL страницы элемента каталога"""
        if self.has_own_page and self.slug:
            return f'/catalog/{self.slug}/'
        return None
    
    def save(self, *args, **kwargs):
        # Автоматически заполняем title из услуги или филиала, если они выбраны и title не указан
        if not self.title:
            if self.service:
                self.title = self.service.title
            elif self.branch:
                self.title = self.branch.name
        
        # Автоматически заполняем описание из услуги, если оно не указано
        if not self.description and self.service:
            self.description = self.service.description
        
        # Автоматически заполняем card_description из услуги, если оно не указано
        if not self.card_description and self.service:
            self.card_description = self.service.short_description or self.service.description
        
        # Автоматически заполняем изображение из услуги или филиала, если оно не указано
        # Примечание: копируем путь к файлу, а не сам файл
        if not self.card_image:
            if self.service and self.service.image:
                # Копируем путь к изображению услуги
                self.card_image = self.service.image
            elif self.branch and self.branch.image:
                # Копируем путь к изображению филиала
                self.card_image = self.branch.image
        
        # Если выбрана услуга, автоматически настраиваем кнопку "Записаться"
        if self.service and self.service.show_booking_button and self.service.booking_form:
            if self.button_type == 'none' or not self.button_type:
                self.button_type = 'booking'
                if not self.button_text:
                    self.button_text = 'Записаться'
                if not self.button_booking_form:
                    self.button_booking_form = self.service.booking_form
        
        if not self.slug and self.has_own_page:
            self.slug = transliterate_slug(self.title) or f'catalog-item-{self.id or 0}'
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для CatalogItem {self.id}: {e}")


class GalleryImage(models.Model):
    """Изображение или видео в галерее"""
    CONTENT_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
    ]
    
    page = models.ForeignKey(ContentPage, on_delete=models.CASCADE, related_name='gallery_images',
                            verbose_name='Страница', help_text='Галерею можно добавить на страницу любого типа')
    content_type = models.CharField('Тип контента', max_length=10, choices=CONTENT_TYPE_CHOICES, default='image',
                                   help_text='Выберите тип контента: изображение или видео')
    image = models.ImageField('Изображение', upload_to='gallery/', blank=True, null=True,
                             help_text='Загрузите изображение (если тип контента - "Изображение")')
    video_file = models.FileField('Видео файл', upload_to='gallery/videos/', blank=True, null=True,
                                 help_text='Загрузите видео файл (если тип контента - "Видео" и хотите загрузить локально)')
    video_url = models.URLField('URL видео', blank=True, null=True,
                               help_text='Ссылка на видео с YouTube, Rutube, Vimeo или другого видеохостинга (если тип контента - "Видео")')
    description = RichTextField('Описание', blank=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Элемент галереи'
        verbose_name_plural = 'Элементы галереи'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        content_type_display = self.get_content_type_display()
        return f'{content_type_display} #{self.id} - {self.page.title}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для GalleryImage {self.id}: {e}")


class FAQItem(models.Model):
    """Элемент FAQ (вопрос-ответ)"""
    page = models.ForeignKey(ContentPage, on_delete=models.CASCADE, related_name='faq_items',
                            verbose_name='Страница FAQ',
                            limit_choices_to={'page_type': 'faq'})
    question = models.CharField('Вопрос', max_length=500)
    answer = RichTextField('Ответ', help_text='Ответ на вопрос с поддержкой форматирования')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Элемент FAQ'
        verbose_name_plural = 'Элементы FAQ'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.question[:50] + ('...' if len(self.question) > 50 else '')


class WelcomeBanner(models.Model):
    WIDTH_CHOICES = [
        ('narrow', 'Узкая (600px)'),
        ('medium', 'Средняя (800px)'),
        ('wide', 'Широкая (1000px)'),
        ('full', 'На всю ширину (1200px)'),
    ]
    
    DISPLAY_TYPE_CHOICES = [
        ('section', 'Раздел сайта'),
        ('modal', 'Модальное окно'),
    ]

    title = models.CharField('Заголовок', max_length=200, blank=True)
    subtitle = RichTextField('Описание', blank=True)
    background_color = models.CharField('Цвет фона', max_length=7, default='#FFFFFF')
    text_color = models.CharField('Цвет текста', max_length=7, default='#1C1C1C')
    content_width = models.CharField('Ширина контента', max_length=10, choices=WIDTH_CHOICES, default='full')
    display_type = models.CharField('Тип отображения', max_length=10, choices=DISPLAY_TYPE_CHOICES, default='section',
                                   help_text='Как будет отображаться баннер: как обычный раздел или модальное окно')
    blur_background = models.IntegerField('Блюр фона под модальным окном', default=0,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         help_text='Уровень размытия фона под модальным окном (0-100%). Работает только для типа "Модальное окно"')
    start_at = models.DateTimeField('Активен с', null=True, blank=True)
    end_at = models.DateTimeField('Активен до', null=True, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Приветственный баннер'
        verbose_name_plural = 'Приветственные баннеры'
        ordering = ['order', '-start_at']

    def __str__(self):
        return self.title or f'Баннер #{self.id}'

    def is_available(self):
        now = timezone.now()
        if self.start_at and now < self.start_at:
            return False
        if self.end_at and now > self.end_at:
            return False
        return True


class WelcomeBannerCard(models.Model):
    BUTTON_TYPES = [
        ('none', 'Без кнопки'),
        ('link', 'Ссылка'),
        ('booking', 'Форма записи'),
        ('quiz', 'Анкета'),
    ]

    banner = models.ForeignKey(WelcomeBanner, on_delete=models.CASCADE, related_name='cards', verbose_name='Баннер')
    title = models.CharField('Заголовок', max_length=200)
    description = RichTextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='welcome_banners/', blank=True, null=True)
    button_type = models.CharField('Тип кнопки', max_length=20, choices=BUTTON_TYPES, default='none')
    button_text = models.CharField('Текст кнопки', max_length=100, blank=True)
    button_url = models.URLField('Ссылка', max_length=500, blank=True)
    button_booking_form = models.ForeignKey('booking.BookingForm', on_delete=models.SET_NULL, null=True, blank=True,
                                            verbose_name='Форма записи', limit_choices_to={'is_active': True})
    button_quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Анкета', limit_choices_to={'is_active': True})
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Карточка приветственного баннера'
        verbose_name_plural = 'Карточки приветственного баннера'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='general')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для WelcomeBannerCard {self.id}: {e}")


class HomePageBlock(models.Model):
    """Блок на главной странице - ссылка на другую страницу контента"""
    TITLE_TAG_CHOICES = [
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
        ('h5', 'H5'),
        ('h6', 'H6'),
    ]
    
    TITLE_ALIGN_CHOICES = [
        ('left', 'Слева'),
        ('center', 'По центру'),
        ('right', 'Справа'),
        ('justify', 'По ширине'),
    ]
    
    TITLE_SIZE_CHOICES = [
        ('small', 'Маленький'),
        ('medium', 'Средний'),
        ('large', 'Большой'),
        ('xlarge', 'Очень большой'),
    ]
    
    page = models.ForeignKey(ContentPage, on_delete=models.CASCADE, related_name='home_blocks',
                            verbose_name='Главная страница', limit_choices_to={'page_type': 'home'})
    content_page = models.ForeignKey(ContentPage, on_delete=models.CASCADE, related_name='+',
                                    verbose_name='Страница для отображения',
                                    help_text='Выберите страницу контента для отображения в этом блоке')
    title = models.CharField('Заголовок блока', max_length=200, blank=True,
                              help_text='Если не указан, будет использован заголовок страницы')
    
    # Настройки отображения заголовка
    show_title = models.BooleanField('Показывать заголовок', default=True,
                                     help_text='Отображать заголовок блока на странице')
    title_tag = models.CharField('Тег заголовка', max_length=2, choices=TITLE_TAG_CHOICES, default='h2',
                                 help_text='HTML тег для заголовка (H1-H6)')
    title_align = models.CharField('Выравнивание', max_length=10, choices=TITLE_ALIGN_CHOICES, default='center',
                                   help_text='Выравнивание заголовка')
    title_size = models.CharField('Размер', max_length=10, choices=TITLE_SIZE_CHOICES, default='large',
                                  help_text='Размер заголовка')
    title_color = models.CharField('Цвет', max_length=7, default='#333333',
                                   help_text='Цвет заголовка в формате HEX (например, #FF820E)')
    title_bold = models.BooleanField('Жирный', default=False)
    title_italic = models.BooleanField('Курсив', default=False)
    title_custom_css = models.TextField('Дополнительные CSS стили', blank=True,
                                       help_text='Дополнительные CSS стили для заголовка (например: text-decoration: underline; margin-bottom: 20px;)')
    
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Блок главной страницы'
        verbose_name_plural = 'Блоки главной страницы'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f'{self.page.title} → {self.content_page.title}'


class Menu(models.Model):
    """Меню - группа пунктов меню для возможности создания нескольких версий"""
    name = models.CharField('Название меню', max_length=100, unique=True,
                            help_text='Например: "Основное меню", "Меню версия 2"')
    description = models.CharField('Описание', max_length=200, blank=True,
                                  help_text='Краткое описание для чего это меню')
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        ordering = ['name']
        app_label = 'content'
    
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Пункт меню"""
    ITEM_TYPE_CHOICES = [
        ('link', 'Обычная ссылка'),
        ('branch_selector', 'Селектор филиала'),
    ]
    
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items',
                            verbose_name='Меню', null=True, blank=True,
                            help_text='Выберите меню, к которому относится этот пункт')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='link',
                                verbose_name='Тип пункта',
                                help_text='Выберите тип пункта меню. "Селектор филиала" отобразит выбор филиала в меню.')
    title = models.CharField('Название (текст)', max_length=100, blank=True,
                            help_text='Оставьте пустым, если используете изображение. Для селектора филиала не используется.')
    image = models.ImageField('Изображение', upload_to='menu/', blank=True, null=True,
                             help_text='Загрузите изображение вместо текста. Для селектора филиала не используется.')
    url = models.CharField('URL', max_length=200, blank=True,
                          help_text='Заполните, если используете внешнюю ссылку или кастомный URL. Для селектора филиала не используется.')
    content_page = models.ForeignKey(ContentPage, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='menu_items', verbose_name='Страница контента',
                                    help_text='Выберите страницу контента, если меню ведет на неё. Для селектора филиала не используется.')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name='Родительский пункт',
                              help_text='Выберите родительский пункт для создания вложенного меню')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    is_external = models.BooleanField('Внешняя ссылка', default=False, 
                                      help_text='Открывать в новой вкладке')

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order', 'title']
        app_label = 'content'

    def __str__(self):
        if self.item_type == 'branch_selector':
            display_name = 'Селектор филиала'
        else:
            display_name = self.title if self.title else (f'Изображение #{self.id}' if self.image else 'Без названия')
        if self.parent:
            return f'{self.parent.title or "Изображение"} → {display_name}'
        return display_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обрабатываем изображение после сохранения
        if self.image and hasattr(self.image, 'file'):
            try:
                process_uploaded_image(self.image, image_type='thumbnail')
                super().save(update_fields=['image'])
            except Exception as e:
                print(f"Ошибка обработки изображения для MenuItem {self.id}: {e}")


class HeaderSettings(models.Model):
    """Настройки шапки"""
    logo_text = models.CharField('Текст логотипа', max_length=100, default='Радуга слов')
    logo_image = models.ImageField('Изображение логотипа', upload_to='logo/', blank=True, null=True, 
                                    help_text='Если загружено, будет использоваться вместо текста')
    logo_url = models.CharField('URL логотипа', max_length=200, default='/', blank=True)
    logo_height = models.IntegerField('Высота логотипа (px)', default=100, 
                                     validators=[MinValueValidator(20), MaxValueValidator(200)],
                                     help_text='Максимальная высота логотипа в пикселях (от 20 до 200)')
    header_height = models.IntegerField('Высота шапки (px)', default=140, 
                                       validators=[MinValueValidator(60), MaxValueValidator(300)],
                                       help_text='Общая высота шапки в пикселях (от 60 до 300). Используется для отступа контента.')
    show_menu = models.BooleanField('Показывать меню', default=True)
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='header_settings', verbose_name='Меню для отображения',
                            help_text='Выберите меню, которое будет отображаться в шапке. Если не выбрано, будет использоваться меню по умолчанию.')
    show_phone = models.BooleanField('Показывать телефон', default=False)
    phone_text = models.CharField('Текст телефона', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Настройки шапки'
        verbose_name_plural = 'Настройки шапки'
        app_label = 'content'

    def __str__(self):
        return 'Настройки шапки'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем логотип после сохранения
        if self.logo_image and hasattr(self.logo_image, 'file'):
            try:
                process_uploaded_image(self.logo_image, image_type='thumbnail')
                super().save(update_fields=['logo_image'])
            except Exception as e:
                print(f"Ошибка обработки логотипа для Header: {e}")


class HeroSettings(models.Model):
    """Настройки Hero секции (шапка главной страницы)"""
    title = models.CharField('Заголовок', max_length=300)
    subtitle = models.TextField('Подзаголовок')
    button_text = models.CharField('Текст кнопки', max_length=100, default='Записаться к логопеду')
    button_url = models.CharField('URL кнопки', max_length=200, default='#contact-form', blank=True,
                                   help_text='Используется только если тип кнопки = "Ссылка"')
    
    BUTTON_TYPE_CHOICES = [
        ('link', 'Ссылка'),
        ('quiz', 'Опрос (анкета)'),
        ('booking', 'Прямая запись'),
    ]
    
    button_type = models.CharField('Тип кнопки', max_length=20, choices=BUTTON_TYPE_CHOICES, default='link',
                                   help_text='Что произойдет при нажатии на кнопку')
    button_quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Анкета для кнопки',
                                    help_text='Выберите анкету, которая откроется при нажатии (если тип = "Опрос")')
    button_booking_form = models.ForeignKey('booking.BookingForm', on_delete=models.SET_NULL, null=True, blank=True,
                                            verbose_name='Форма записи для кнопки',
                                            help_text='Выберите форму записи, которая откроется при нажатии (если тип = "Прямая запись")')
    background_image = models.ImageField('Фоновое изображение', upload_to='hero/', blank=True, null=True,
                                         help_text='Фоновое изображение для Hero секции')
    background_color = models.CharField('Цвет фона', max_length=7, default='#FF820E',
                                        help_text='Цвет фона (если изображение не загружено или для наложения)')
    
    IMAGE_POSITION_CHOICES = [
        ('left', 'Слева'),
        ('center', 'По центру'),
        ('right', 'Справа'),
    ]
    
    IMAGE_VERTICAL_ALIGN_CHOICES = [
        ('top', 'Сверху'),
        ('center', 'По середине'),
        ('bottom', 'Снизу'),
    ]
    
    IMAGE_SIZE_CHOICES = [
        ('cover', 'Растянуть (cover)'),
        ('contain', 'Вместить (contain)'),
        ('auto', 'Автоматически'),
        ('100%', '100% размера'),
    ]
    
    image_position = models.CharField('Горизонтальное выравнивание', max_length=20, choices=IMAGE_POSITION_CHOICES,
                                      default='right', help_text='Горизонтальное расположение изображения (слева, по центру, справа)')
    image_vertical_align = models.CharField('Вертикальное выравнивание', max_length=20, choices=IMAGE_VERTICAL_ALIGN_CHOICES,
                                            default='center', help_text='Вертикальное расположение изображения (сверху, по середине, снизу)')
    image_size = models.CharField('Размер изображения', max_length=20, choices=IMAGE_SIZE_CHOICES,
                                  default='cover', help_text='Как изображение должно заполнять область')
    image_scale = models.DecimalField('Масштаб изображения (%)', max_digits=5, decimal_places=2,
                                      default=100.00, validators=[MinValueValidator(10.00), MaxValueValidator(500.00)],
                                      help_text='Масштаб изображения в процентах (от 10% до 500%)')
    show_overlay = models.BooleanField('Показывать затемнение', default=True,
                                       help_text='Темный оверлей для лучшей читаемости текста')
    overlay_opacity = models.DecimalField('Прозрачность затемнения', max_digits=3, decimal_places=2,
                                          default=0.30,
                                          help_text='От 0.00 (прозрачно) до 1.00 (полностью непрозрачно)')
    
    TEXT_ALIGN_CHOICES = [
        ('left', 'По левому краю'),
        ('center', 'По центру'),
        ('right', 'По правому краю'),
    ]
    text_align = models.CharField('Выравнивание текста', max_length=10, choices=TEXT_ALIGN_CHOICES,
                                  default='left', help_text='Выравнивание заголовка и подзаголовка')
    
    CONTENT_WIDTH_CHOICES = [
        ('narrow', 'Узкая (600px)'),
        ('medium', 'Средняя (800px)'),
        ('wide', 'Широкая (1000px)'),
        ('full', 'На всю ширину (1200px)'),
        ('custom', 'Произвольная'),
    ]
    
    content_width = models.CharField('Ширина контента', max_length=20, choices=CONTENT_WIDTH_CHOICES,
                                     default='narrow', help_text='Ширина полезной области для текста в Hero секции')
    content_width_custom = models.IntegerField('Произвольная ширина (px)', null=True, blank=True,
                                                validators=[MinValueValidator(300), MaxValueValidator(2000)],
                                                help_text='Используется только если выбрана "Произвольная" ширина (от 300 до 2000px)')
    
    is_active = models.BooleanField('Активна', default=True)
    
    class Meta:
        verbose_name = 'Настройки Hero'
        verbose_name_plural = 'Настройки Hero'
        app_label = 'content'

    def __str__(self):
        return 'Настройки Hero'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        
        # Сохраняем сначала
        super().save(*args, **kwargs)
        # Обрабатываем фоновое изображение после сохранения
        if self.background_image and hasattr(self.background_image, 'file'):
            try:
                process_uploaded_image(self.background_image, image_type='hero')
                super().save(update_fields=['background_image'])
            except Exception as e:
                print(f"Ошибка обработки фонового изображения для Hero: {e}")


class SocialNetwork(models.Model):
    """Социальная сеть"""
    NETWORK_TYPES = [
        ('vk', 'ВКонтакте'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter'),
        ('ok', 'Одноклассники'),
        ('custom', 'Другая'),
    ]
    
    name = models.CharField('Название', max_length=100,
                           help_text='Название соцсети для отображения')
    network_type = models.CharField('Тип соцсети', max_length=20, choices=NETWORK_TYPES, default='custom',
                                    help_text='Выберите тип соцсети или "Другая" для кастомной')
    url = models.URLField('URL', max_length=500,
                         help_text='Ссылка на профиль/канал в соцсети')
    icon = models.ImageField('Иконка', upload_to='social/', blank=True, null=True,
                             help_text='Иконка соцсети (если не указана, будет использована стандартная)')
    order = models.IntegerField('Порядок', default=0,
                               help_text='Порядок отображения в списке')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Социальная сеть'
        verbose_name_plural = 'Социальные сети'
        ordering = ['order', 'name']
        app_label = 'content'
    
    def __str__(self):
        return self.name


class FooterSettings(models.Model):
    """Настройки подвала"""
    copyright_text = models.CharField('Текст копирайта', max_length=200, 
                                      default='© 2024. Все права защищены')
    show_contacts = models.BooleanField('Показывать контакты', default=True)
    show_navigation = models.BooleanField('Показывать навигацию', default=True)
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='footer_settings', verbose_name='Меню для отображения',
                            help_text='Выберите меню, которое будет отображаться в футере. Если не выбрано, будет использоваться меню по умолчанию.')
    show_social = models.BooleanField('Показывать соцсети', default=False)
    additional_text = models.TextField('Дополнительный текст', blank=True)
    
    class Meta:
        verbose_name = 'Настройки подвала'
        verbose_name_plural = 'Настройки подвала'
        app_label = 'content'

    def __str__(self):
        return 'Настройки подвала'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        super().save(*args, **kwargs)


class PrivacyPolicy(models.Model):
    """Политика (конфиденциальности, авторских прав и т.д.)"""
    title = models.CharField('Заголовок', max_length=200, 
                            help_text='Например: Политика конфиденциальности, Защита авторских прав')
    slug = models.SlugField('URL-адрес', max_length=200, unique=True,
                           help_text='Используется в URL страницы (например: privacy, copyright)')
    content = models.TextField('Содержание')
    order = models.IntegerField('Порядок', default=0,
                               help_text='Порядок отображения в списке')
    is_published = models.BooleanField('Опубликована', default=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Политика'
        verbose_name_plural = 'Политики'
        ordering = ['order', 'title']
        app_label = 'content'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Возвращает URL страницы политики"""
        return f'/policies/{self.slug}/'


class SiteSettings(models.Model):
    """Глобальные настройки сайта"""
    primary_color = models.CharField('Основной цвет', max_length=7, default='#667eea',
                                    help_text='Основной цвет сайта (HEX)')
    gradient_start = models.CharField('Начало градиента', max_length=7, default='#667eea',
                                     help_text='Цвет начала градиента (HEX)')
    gradient_end = models.CharField('Конец градиента', max_length=7, default='#764ba2',
                                   help_text='Цвет конца градиента (HEX)')
    secondary_color = models.CharField('Вторичный цвет', max_length=7, default='#764ba2', blank=True,
                                       help_text='Вторичный цвет для акцентов (HEX)')
    text_color = models.CharField('Цвет текста', max_length=7, default='#333333', blank=True,
                                 help_text='Основной цвет текста (HEX)')
    background_color = models.CharField('Цвет фона', max_length=7, default='#ffffff', blank=True,
                                       help_text='Цвет фона страницы (HEX)')
    
    class Meta:
        verbose_name = 'Настройки цвета сайта'
        verbose_name_plural = 'Настройки цвета сайта'

    def __str__(self):
        return 'Настройки цвета сайта'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        super().save(*args, **kwargs)
