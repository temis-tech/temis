from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .utils.image_processing import process_uploaded_image
import re


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
    description = models.TextField('Описание')
    short_description = models.TextField('Краткое описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_with_abonement = models.DecimalField('Цена по абонементу', max_digits=10, decimal_places=2, 
                                                validators=[MinValueValidator(0)], blank=True, null=True)
    duration = models.CharField('Длительность', max_length=50, default='45 минут')
    image = models.ImageField('Изображение', upload_to='services/', blank=True, null=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
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


class MenuItem(models.Model):
    """Пункт меню"""
    title = models.CharField('Название (текст)', max_length=100, blank=True,
                            help_text='Оставьте пустым, если используете изображение')
    image = models.ImageField('Изображение', upload_to='menu/', blank=True, null=True,
                             help_text='Загрузите изображение вместо текста')
    url = models.CharField('URL', max_length=200, help_text='Например: /services или http://example.com')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name='Родительский пункт',
                              help_text='Выберите родительский пункт для создания вложенного меню')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    is_external = models.BooleanField('Внешняя ссылка', default=False, 
                                      help_text='Открывать в новой вкладке')

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Меню'
        ordering = ['order', 'title']

    def __str__(self):
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
    show_phone = models.BooleanField('Показывать телефон', default=False)
    phone_text = models.CharField('Текст телефона', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'Настройки шапки'
        verbose_name_plural = 'Настройки шапки'

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
        ('quiz', 'Опрос (квиз)'),
        ('booking', 'Прямая запись'),
    ]
    
    button_type = models.CharField('Тип кнопки', max_length=20, choices=BUTTON_TYPE_CHOICES, default='link',
                                   help_text='Что произойдет при нажатии на кнопку')
    button_quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Квиз для кнопки',
                                    help_text='Выберите квиз, который откроется при нажатии (если тип = "Опрос")')
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
    
    is_active = models.BooleanField('Активна', default=True)
    
    class Meta:
        verbose_name = 'Настройки Hero'
        verbose_name_plural = 'Настройки Hero'

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


class FooterSettings(models.Model):
    """Настройки подвала"""
    copyright_text = models.CharField('Текст копирайта', max_length=200, 
                                      default='© 2024. Все права защищены')
    show_contacts = models.BooleanField('Показывать контакты', default=True)
    show_navigation = models.BooleanField('Показывать навигацию', default=True)
    show_social = models.BooleanField('Показывать соцсети', default=False)
    additional_text = models.TextField('Дополнительный текст', blank=True)
    
    class Meta:
        verbose_name = 'Настройки подвала'
        verbose_name_plural = 'Настройки подвала'

    def __str__(self):
        return 'Настройки подвала'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        super().save(*args, **kwargs)


class PrivacyPolicy(models.Model):
    """Политика конфиденциальности"""
    title = models.CharField('Заголовок', max_length=200, default='Политика конфиденциальности')
    content = models.TextField('Содержание')
    is_published = models.BooleanField('Опубликована', default=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Политика конфиденциальности'
        verbose_name_plural = 'Политика конфиденциальности'

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        super().save(*args, **kwargs)


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
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'
    
    def save(self, *args, **kwargs):
        # Разрешаем только одну запись
        self.pk = 1
        super().save(*args, **kwargs)
