from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import (
    Contact,
    Menu, MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings,
    ContentPage, CatalogItem, GalleryImage, HomePageBlock,
    WelcomeBanner, WelcomeBannerCard, SocialNetwork
)


# ==================== КОНТАКТЫ ====================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['phone', 'phone_secondary', 'email', 'is_active']
    list_editable = ['is_active']


# ==================== КОНСТРУКТОР СТРАНИЦ ====================
class CatalogItemInline(admin.TabularInline):
    model = CatalogItem
    extra = 1
    fields = ['title', 'width', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ['image', 'description', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


class HomePageBlockInline(admin.TabularInline):
    model = HomePageBlock
    extra = 1
    fields = ['content_page', 'title', 'show_title', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_type', 'slug', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']
    list_filter = ['page_type', 'is_active', 'created_at']
    search_fields = ['title', 'slug', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['image_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'page_type', 'description')
        }),
        ('Изображение (для типа "Описание")', {
            'fields': ('image', 'image_preview', 'image_align', 'image_size'),
            'description': 'Настройки изображения для страниц типа "Описание". Изображение будет отображаться вместе с описанием.'
        }),
        ('Отображение', {
            'fields': ('show_title',),
            'description': 'Настройки отображения страницы на сайте'
        }),
        ('Настройки', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью изображения'
    
    def get_inlines(self, request, obj):
        """Показываем разные inline в зависимости от типа страницы"""
        if obj and obj.pk:
            if obj.page_type == 'catalog':
                return [CatalogItemInline]
            elif obj.page_type == 'gallery':
                return [GalleryImageInline]
            elif obj.page_type == 'home':
                return [HomePageBlockInline]
        return []


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'page', 'width', 'has_own_page', 'slug', 'button_type', 'order', 'is_active', 'image_preview']
    list_editable = ['order', 'is_active', 'has_own_page', 'width']
    list_filter = ['page', 'has_own_page', 'button_type', 'is_active', 'width']
    search_fields = ['title', 'description', 'slug']
    readonly_fields = ['image_preview']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'title', 'description', 'image', 'image_preview')
        }),
        ('Настройки изображения', {
            'fields': ('image_align', 'image_size'),
            'description': 'Настройте выравнивание и размер изображения для красивого размещения контента.'
        }),
        ('Размер и расположение', {
            'fields': ('width',),
            'description': 'Ширина элемента в сетке каталога. Узкая - 1/3 ширины, Средняя - 1/2, Широкая - 2/3, На всю ширину - 100%.'
        }),
        ('Страница элемента', {
            'fields': ('has_own_page', 'slug'),
            'description': 'Включите "Может быть открыт как страница", чтобы карточка имела свой URL и могла быть открыта как отдельная страница. URL будет автоматически сгенерирован из названия.'
        }),
        ('Кнопка', {
            'fields': ('button_type', 'button_text', 'button_booking_form', 'button_quiz', 'button_url'),
            'description': 'Настройте тип кнопки и соответствующие параметры. Для типа "Форма записи" выберите форму из списка. Для типа "Анкета" выберите анкету. Для типа "Внешняя ссылка" укажите URL.'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['page', 'order', 'is_active', 'image_preview', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['page', 'is_active', 'created_at']
    readonly_fields = ['image_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'image', 'image_preview', 'description')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(HomePageBlock)
class HomePageBlockAdmin(admin.ModelAdmin):
    list_display = ['page', 'content_page', 'title', 'show_title', 'title_tag', 'title_align', 'order', 'is_active']
    list_editable = ['order', 'is_active', 'show_title']
    list_filter = ['page', 'is_active', 'show_title', 'title_tag', 'title_align']
    search_fields = ['title', 'content_page__title']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'content_page', 'title')
        }),
        ('Настройки отображения заголовка', {
            'fields': ('show_title', 'title_tag', 'title_align', 'title_size', 
                      'title_color', 'title_bold', 'title_italic', 'title_custom_css'),
            'description': 'Настройте внешний вид заголовка блока на главной странице'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )


class WelcomeBannerCardInline(admin.TabularInline):
    model = WelcomeBannerCard
    extra = 1
    fields = [
        'title', 'description', 'image', 'button_type', 'button_text',
        'button_url', 'button_booking_form', 'button_quiz', 'order', 'is_active'
    ]
    show_change_link = True


@admin.register(WelcomeBanner)
class WelcomeBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_type', 'is_active', 'start_at', 'end_at', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'display_type', 'content_width', 'start_at', 'end_at']
    search_fields = ['title', 'subtitle']
    inlines = [WelcomeBannerCardInline]

    fieldsets = (
        ('Контент', {
            'fields': ('title', 'subtitle')
        }),
        ('Оформление', {
            'fields': ('background_color', 'text_color', 'content_width')
        }),
        ('Тип отображения', {
            'fields': ('display_type', 'blur_background'),
            'description': 'Выберите, как будет отображаться баннер. Для модального окна можно настроить размытие фона.'
        }),
        ('Доступность', {
            'fields': ('start_at', 'end_at', 'is_active', 'order'),
            'description': 'Укажите временной период, в течение которого баннер будет отображаться'
        }),
    )


# ==================== НАСТРОЙКИ САЙТА ====================
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'items_count', 'created_at']
    list_editable = ['is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
    )
    
    def items_count(self, obj):
        return obj.items.filter(is_active=True).count()
    items_count.short_description = 'Активных пунктов'


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ['title', 'image', 'content_page', 'url', 'parent', 'order', 'is_active', 'is_external']
    show_change_link = True


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'menu', 'parent', 'url', 'order', 'is_active', 'is_external', 'image_preview']
    list_editable = ['order', 'is_active', 'is_external']
    list_filter = ['menu', 'is_active', 'parent']
    search_fields = ['title', 'url']
    list_display_links = ['display_name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('menu', 'title', 'image', 'image_preview', 'content_page', 'url', 'parent'),
            'description': 'Укажите либо текст (title), либо загрузите изображение. Выберите страницу контента или укажите URL вручную.'
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
    list_display = ['logo_text', 'logo_height', 'header_height', 'show_menu', 'menu', 'show_phone']
    fieldsets = (
        ('Логотип', {
            'fields': ('logo_text', 'logo_image', 'logo_url', 'logo_height', 'logo_preview')
        }),
        ('Размеры', {
            'fields': ('header_height',),
            'description': 'Высота шапки используется для расчета отступа контента, чтобы он не перекрывался фиксированной шапкой.'
        }),
        ('Меню', {
            'fields': ('show_menu', 'menu'),
            'description': 'Выберите меню, которое будет отображаться в шапке. Можно создать несколько меню для тестирования разных версий.'
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
            'description': 'Настройте действие кнопки: ссылка, открытие анкеты или формы записи. Если выбран тип "Ссылка", укажите URL. Если "Анкета" - выберите её. Если "Прямая запись" - выберите форму.'
        }),
        ('Внешний вид', {
            'fields': ('background_image', 'image_preview', 'background_color')
        }),
        ('Настройки изображения', {
            'fields': ('image_position', 'image_vertical_align', 'image_size', 'image_scale', 'show_overlay', 'overlay_opacity'),
            'description': 'Настройте расположение (горизонтальное и вертикальное), размер и масштаб фонового изображения, а также затемнение для читаемости текста.'
        }),
        ('Настройки текста', {
            'fields': ('text_align', 'content_width', 'content_width_custom'),
            'description': 'Выберите выравнивание заголовка и подзаголовка, а также ширину полезной области для текста.'
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


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'network_type', 'url', 'order', 'is_active', 'icon_preview']
    list_editable = ['order', 'is_active']
    list_filter = ['network_type', 'is_active']
    search_fields = ['name', 'url']
    readonly_fields = ['icon_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'network_type', 'url', 'icon', 'icon_preview')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def icon_preview(self, obj):
        if obj and obj.icon:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; object-fit: contain;" />',
                obj.icon.url
            )
        return "Нет иконки (будет использована стандартная)"
    icon_preview.short_description = 'Превью иконки'


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = ['copyright_text', 'show_contacts', 'show_navigation', 'menu', 'show_social']
    fieldsets = (
        ('Копирайт', {
            'fields': ('copyright_text',)
        }),
        ('Отображение', {
            'fields': ('show_contacts', 'show_navigation', 'menu', 'show_social'),
            'description': 'Выберите меню, которое будет отображаться в футере. Можно создать несколько меню для тестирования разных версий. Для отображения соцсетей создайте их в разделе "Социальные сети".'
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
    list_display = ['title', 'slug', 'order', 'is_published', 'is_active', 'created_at', 'updated_at']
    list_editable = ['order', 'is_published', 'is_active']
    list_filter = ['is_published', 'is_active', 'created_at']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'order')
        }),
        ('Контент', {
            'fields': ('content',)
        }),
        ('Настройки', {
            'fields': ('is_published', 'is_active')
        }),
    )


# Группировка в админке
admin.site.site_header = 'Администрирование сайта "Радуга слов"'
admin.site.site_title = 'Радуга слов'
admin.site.index_title = 'Панель управления'

# Кастомная группировка моделей через переопределение get_app_list
import types

def custom_get_app_list(self, request, app_label=None):
    """
    Возвращает список приложений с кастомной группировкой моделей content
    
    Args:
        request: HTTP request
        app_label: Optional app label when viewing a specific app
    """
    app_dict = {}
    
    # Получаем все зарегистрированные модели
    for model, model_admin in self._registry.items():
        app_label = model._meta.app_label
        
        # Группируем модели content по категориям
        if app_label == 'content':
            # Определяем категорию модели
            if model == Contact:
                category = 'Контакты'
            elif model in [ContentPage, CatalogItem, GalleryImage, HomePageBlock, WelcomeBanner]:
                category = 'Контент'
            elif model in [HeaderSettings, Menu, MenuItem, FooterSettings, SocialNetwork]:
                category = 'Шапка и Подвал'
            elif model in [HeroSettings, SiteSettings]:
                category = 'Настройки цвета сайта'
            elif model == PrivacyPolicy:
                category = 'Политики'
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
        if app['name'] == 'Контент':
            # Кастомный порядок для раздела "Контент"
            content_order = {
                'Блоки главной страницы': 1,
                'Страницы контента': 2,
                'Изображения галереи': 3,
                'Элементы каталога': 4,
                'Приветственные баннеры': 5,
            }
            app['models'].sort(key=lambda x: content_order.get(x['name'], 999))
        else:
            # Для остальных разделов сортируем по имени
            app['models'].sort(key=lambda x: x['name'])
    
    return app_list

# Переопределяем метод get_app_list
admin.site.get_app_list = types.MethodType(custom_get_app_list, admin.site)
