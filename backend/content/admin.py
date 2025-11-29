from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import (
    Branch, Service, Specialist, Review, Promotion, Article, Contact,
    MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings
)


# ==================== КОНТЕНТ САЙТА ====================
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'metro', 'phone', 'order', 'is_active', 'image_preview']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'address']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 100px; max-height: 100px;" />'
        return "Нет изображения"
    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'price_with_abonement', 'duration', 'order', 'is_active', 
                   'show_booking_button', 'image_preview']
    list_editable = ['order', 'is_active', 'show_booking_button']
    list_filter = ['is_active', 'show_booking_button']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['image_preview']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'short_description', 'image', 'image_preview')
        }),
        ('Цены и длительность', {
            'fields': ('price', 'price_with_abonement', 'duration')
        }),
        ('Запись на услугу', {
            'fields': ('show_booking_button', 'booking_form')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def image_preview(self, obj):
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 100px; max-height: 100px;" />'
        return "Нет изображения"
    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'branch', 'order', 'is_active', 'photo_preview']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'branch']
    search_fields = ['name', 'position']
    readonly_fields = ['photo_preview']
    
    def photo_preview(self, obj):
        if obj and obj.photo:
            return f'<img src="{obj.photo.url}" style="max-width: 100px; max-height: 100px; border-radius: 50%;" />'
        return "Нет фото"
    photo_preview.allow_tags = True
    photo_preview.short_description = 'Фото'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'rating', 'is_published', 'order', 'created_at', 'photo_preview']
    list_editable = ['is_published', 'order']
    list_filter = ['is_published', 'rating']
    search_fields = ['author_name', 'text']
    readonly_fields = ['photo_preview']
    
    def photo_preview(self, obj):
        if obj and obj.author_photo:
            return f'<img src="{obj.author_photo.url}" style="max-width: 100px; max-height: 100px; border-radius: 50%;" />'
        return "Нет фото"
    photo_preview.allow_tags = True
    photo_preview.short_description = 'Фото'


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'order', 'image_preview']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 100px; max-height: 100px;" />'
        return "Нет изображения"
    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'views_count', 'created_at', 'image_preview']
    list_editable = ['is_published']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['image_preview']
    
    def get_queryset(self, request):
        """Возвращает все статьи, включая неопубликованные"""
        qs = super().get_queryset(request)
        return qs  # Показываем все статьи в админке
    
    def image_preview(self, obj):
        if obj and obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 100px; max-height: 100px;" />'
        return "Нет изображения"
    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'


# ==================== КОНТАКТЫ ====================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['phone', 'phone_secondary', 'email', 'is_active']
    list_editable = ['is_active']


# ==================== НАСТРОЙКИ САЙТА ====================
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'parent', 'url', 'order', 'is_active', 'is_external', 'image_preview']
    list_editable = ['order', 'is_active', 'is_external']
    list_filter = ['is_active', 'parent']
    search_fields = ['title', 'url']
    list_display_links = ['display_name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'image', 'image_preview', 'url', 'parent'),
            'description': 'Укажите либо текст (title), либо загрузите изображение. Если указаны оба, приоритет у изображения.'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active', 'is_external')
        }),
    )
    
    readonly_fields = ['image_preview']
    
    def display_name(self, obj):
        """Отображает название или информацию об изображении"""
        if obj.image:
            return f'🖼️ Изображение #{obj.id}'
        return obj.title or 'Без названия'
    display_name.short_description = 'Название'
    
    def image_preview(self, obj):
        """Превью изображения в админке"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью изображения'


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    list_display = ['logo_text', 'logo_height', 'header_height', 'show_menu', 'show_phone']
    fieldsets = (
        ('Логотип', {
            'fields': ('logo_text', 'logo_image', 'logo_url', 'logo_height', 'logo_preview')
        }),
        ('Размеры', {
            'fields': ('header_height',),
            'description': 'Высота шапки используется для расчета отступа контента, чтобы он не перекрывался фиксированной шапкой.'
        }),
        ('Меню', {
            'fields': ('show_menu',)
        }),
        ('Телефон', {
            'fields': ('show_phone', 'phone_text')
        }),
    )
    readonly_fields = ['logo_preview']
    
    def logo_preview(self, obj):
        if obj and obj.logo_image:
            return f'<img src="{obj.logo_image.url}" style="max-width: 200px; max-height: 100px;" />'
        return "Нет изображения (будет использован текст)"
    logo_preview.allow_tags = True
    logo_preview.short_description = 'Превью логотипа'
    
    def has_add_permission(self, request):
        return not HeaderSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSettings)
class HeroSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'button_text', 'button_type', 'image_position', 'is_active']
    fieldsets = (
        ('Контент', {
            'fields': ('title', 'subtitle'),
            'description': 'Поля "Заголовок" и "Подзаголовок" поддерживают HTML форматирование. Можно использовать теги: <strong>, <em>, <br>, <p>, <span style="color: #FF820E;"> и др.'
        }),
        ('Кнопка', {
            'fields': ('button_text', 'button_type', 'button_url', 'button_quiz', 'button_booking_form'),
            'description': 'Настройте действие кнопки: ссылка, открытие квиза или формы записи. Если выбран тип "Ссылка", укажите URL. Если "Опрос" - выберите квиз. Если "Прямая запись" - выберите форму записи.'
        }),
        ('Внешний вид', {
            'fields': ('background_image', 'image_preview', 'background_color')
        }),
        ('Настройки изображения', {
            'fields': ('image_position', 'image_vertical_align', 'image_size', 'image_scale', 'show_overlay', 'overlay_opacity'),
            'description': 'Настройте расположение (горизонтальное и вертикальное), размер и масштаб фонового изображения, а также затемнение для читаемости текста.'
        }),
        ('Настройки текста', {
            'fields': ('text_align',),
            'description': 'Выберите выравнивание заголовка и подзаголовка.'
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ['image_preview']
    
    class Media:
        css = {
            'all': ('admin/css/colorpicker.css',)
        }
        js = ('admin/js/colorpicker.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Добавляем атрибуты для color picker
        if 'background_color' in form.base_fields:
            form.base_fields['background_color'].widget.attrs.update({
                'type': 'color',
                'style': 'width: 100px; height: 40px;'
            })
        # Увеличиваем размер полей title и subtitle для удобства редактирования HTML
        if 'title' in form.base_fields:
            form.base_fields['title'].widget.attrs.update({
                'rows': 3,
                'style': 'width: 100%; font-family: monospace;'
            })
        if 'subtitle' in form.base_fields:
            form.base_fields['subtitle'].widget.attrs.update({
                'rows': 6,
                'style': 'width: 100%; font-family: monospace;'
            })
        # Добавляем слайдер для масштаба изображения
        if 'image_scale' in form.base_fields:
            form.base_fields['image_scale'].widget.attrs.update({
                'type': 'range',
                'min': '10',
                'max': '500',
                'step': '1',
                'style': 'width: 300px;'
            })
        return form
    
    def image_preview(self, obj):
        if obj and obj.background_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain;" />',
                obj.background_image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью фонового изображения'
    
    def has_add_permission(self, request):
        return not HeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = ['copyright_text', 'show_contacts', 'show_navigation']
    fieldsets = (
        ('Копирайт', {
            'fields': ('copyright_text',)
        }),
        ('Отображение', {
            'fields': ('show_contacts', 'show_navigation', 'show_social')
        }),
        ('Дополнительно', {
            'fields': ('additional_text',)
        }),
    )
    
    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['primary_color', 'gradient_start', 'gradient_end', 'color_preview']
    fieldsets = (
        ('Цвета', {
            'fields': ('primary_color', 'secondary_color', 'text_color', 'background_color')
        }),
        ('Градиенты', {
            'fields': ('gradient_start', 'gradient_end', 'gradient_preview')
        }),
    )
    readonly_fields = ['color_preview', 'gradient_preview']
    
    class Media:
        css = {
            'all': ('admin/css/colorpicker.css',)
        }
        js = (
            'admin/js/colorpicker.js',
        )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Делаем поля цвета более удобными
        for field_name in ['primary_color', 'secondary_color', 'text_color', 'background_color', 
                          'gradient_start', 'gradient_end']:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget.attrs.update({
                    'placeholder': '#667eea',
                    'pattern': '^#[0-9A-Fa-f]{6}$',
                    'title': 'Введите цвет в формате HEX (например: #667eea)'
                })
        return form
    
    def color_preview(self, obj):
        if obj:
            return format_html(
                '<div style="display: flex; gap: 1rem; margin-top: 0.5rem; align-items: center;">'
                '<div><strong>Основной:</strong><div style="width: 60px; height: 60px; background: {}; border: 2px solid #ddd; border-radius: 8px; margin-top: 0.25rem;"></div></div>'
                '<div><strong>Вторичный:</strong><div style="width: 60px; height: 60px; background: {}; border: 2px solid #ddd; border-radius: 8px; margin-top: 0.25rem;"></div></div>'
                '<div><strong>Текст:</strong><div style="width: 60px; height: 60px; background: {}; border: 2px solid #ddd; border-radius: 8px; margin-top: 0.25rem;"></div></div>'
                '</div>',
                obj.primary_color or '#667eea',
                obj.secondary_color or '#764ba2',
                obj.text_color or '#333333'
            )
        return "Нет настроек"
    color_preview.short_description = 'Превью цветов'
    
    def gradient_preview(self, obj):
        if obj:
            return format_html(
                '<div style="width: 100%; height: 80px; background: linear-gradient(135deg, {} 0%, {} 100%); border-radius: 8px; margin-top: 0.5rem; border: 2px solid #ddd;"></div>',
                obj.gradient_start or '#667eea',
                obj.gradient_end or '#764ba2'
            )
        return "Нет настроек"
    gradient_preview.short_description = 'Превью градиента'
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'updated_at']
    list_editable = ['is_published']
    fieldsets = (
        ('Контент', {
            'fields': ('title', 'content', 'is_published')
        }),
    )
    
    def has_add_permission(self, request):
        return not PrivacyPolicy.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# Группировка в админке
admin.site.site_header = 'Администрирование сайта "Радуга слов"'
admin.site.site_title = 'Радуга слов'
admin.site.index_title = 'Панель управления'

# Кастомная группировка моделей через переопределение get_app_list
import types

def custom_get_app_list(self, request):
    """
    Возвращает список приложений с кастомной группировкой моделей content
    """
    app_dict = {}
    
    # Получаем все зарегистрированные модели
    for model, model_admin in self._registry.items():
        app_label = model._meta.app_label
        
        # Группируем модели content по категориям
        if app_label == 'content':
            # Определяем категорию модели
            if model in [Branch, Service, Specialist, Review, Promotion, Article]:
                category = 'Контент сайта'
            elif model == Contact:
                category = 'Контакты'
            elif model in [MenuItem, HeaderSettings, HeroSettings, FooterSettings, SiteSettings, PrivacyPolicy]:
                category = 'Настройки сайта'
            else:
                category = 'Контент'
            
            # Используем оригинальный app_label для URL, но кастомное имя для отображения
            display_name = category
            url_app_label = app_label
            
            if category not in app_dict:
                app_dict[category] = {
                    'name': display_name,
                    'app_label': url_app_label,  # Используем оригинальный app_label для URL
                    'app_url': f'/admin/{url_app_label}/',
                    'has_module_perms': request.user.has_module_perms(url_app_label),
                    'models': []
                }
            
            app_dict[category]['models'].append({
                'name': model._meta.verbose_name_plural,
                'object_name': model.__name__,
                'perms': {
                    'add': request.user.has_perm(f'{url_app_label}.add_{model._meta.model_name}'),
                    'change': request.user.has_perm(f'{url_app_label}.change_{model._meta.model_name}'),
                    'delete': request.user.has_perm(f'{url_app_label}.delete_{model._meta.model_name}'),
                    'view': request.user.has_perm(f'{url_app_label}.view_{model._meta.model_name}'),
                },
                'admin_url': f'/admin/{url_app_label}/{model._meta.model_name}/',
                'add_url': f'/admin/{url_app_label}/{model._meta.model_name}/add/',
            })
        else:
            # Для других приложений используем стандартную логику
            if app_label not in app_dict:
                from django.apps import apps
                try:
                    app_config = apps.get_app_config(app_label)
                    app_name = app_config.verbose_name or app_label
                except:
                    app_name = app_label
                
                app_dict[app_label] = {
                    'name': app_name,
                    'app_label': app_label,
                    'app_url': f'/admin/{app_label}/',
                    'has_module_perms': request.user.has_module_perms(app_label),
                    'models': []
                }
            
            app_dict[app_label]['models'].append({
                'name': model._meta.verbose_name_plural,
                'object_name': model.__name__,
                'perms': {
                    'add': request.user.has_perm(f'{app_label}.add_{model._meta.model_name}'),
                    'change': request.user.has_perm(f'{app_label}.change_{model._meta.model_name}'),
                    'delete': request.user.has_perm(f'{app_label}.delete_{model._meta.model_name}'),
                    'view': request.user.has_perm(f'{app_label}.view_{model._meta.model_name}'),
                },
                'admin_url': f'/admin/{app_label}/{model._meta.model_name}/',
                'add_url': f'/admin/{app_label}/{model._meta.model_name}/add/',
            })
    
    # Сортируем приложения
    app_list = sorted(app_dict.values(), key=lambda x: x['name'])
    
    # Сортируем модели внутри каждого приложения
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])
    
    return app_list

# Переопределяем метод get_app_list
admin.site.get_app_list = types.MethodType(custom_get_app_list, admin.site)
