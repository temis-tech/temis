from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import (
    Contact, Branch, Service, ServiceBranch, ServiceBranchPriceHistory,
    Menu, MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings,
    ContentPage, CatalogItem, GalleryImage, HomePageBlock, FAQItem,
    WelcomeBanner, WelcomeBannerCard, SocialNetwork
)


# ==================== КОНТАКТЫ ====================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['phone', 'phone_secondary', 'email', 'is_active']
    list_editable = ['is_active']


# ==================== ФИЛИАЛЫ ====================
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'metro', 'address', 'phone', 'order', 'is_active', 'content_page', 'image_preview']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at', 'content_page']
    search_fields = ['name', 'address', 'metro', 'phone']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'address', 'metro', 'phone', 'image', 'image_preview')
        }),
        ('Страница филиала', {
            'fields': ('content_page',),
            'description': 'Выберите страницу контента для отображения информации о филиале через конструктор. Это позволит создать отдельную страницу для филиала с описанием, галереей и другими элементами. При выборе филиала в меню пользователь будет автоматически перенаправлен на эту страницу.'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active', 'created_at', 'updated_at')
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


# ==================== КОНСТРУКТОР СТРАНИЦ ====================
class CatalogItemInline(admin.TabularInline):
    model = CatalogItem
    extra = 0
    fields = ['title', 'width', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0
    fields = ['content_type', 'image', 'video_file', 'video_url', 'description', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


class HomePageBlockInline(admin.TabularInline):
    model = HomePageBlock
    extra = 0
    fields = ['content_page', 'title', 'show_title', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 0
    fields = ['question', 'answer', 'order', 'is_active']
    show_change_link = True
    fk_name = 'page'


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_type', 'slug', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']
    list_filter = ['page_type', 'is_active', 'created_at']
    search_fields = ['title', 'slug', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['image_preview', 'faq_icon_preview', 'faq_background_image_preview']
    # Inline формы для каталога и галереи доступны на всех страницах
    inlines = [CatalogItemInline, GalleryImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'page_type', 'description')
        }),
        ('Изображение (для типа "Описание")', {
            'fields': ('image', 'image_preview', 'image_align', 'image_size'),
            'description': 'Настройки изображения для страниц типа "Описание". Изображение будет отображаться вместе с описанием.'
        }),
        ('Каталог и Галерея (для типа "Описание")', {
            'fields': ('selected_catalog_page', 'selected_gallery_page'),
            'description': 'Выберите страницу каталога или галереи для отображения на этой странице. Можно выбрать только одну из них или обе. Если выбраны обе, они будут отображаться последовательно.'
        }),
        ('Настройки галереи (для типа "Галерея")', {
            'fields': ('gallery_display_type', 'gallery_enable_fullscreen'),
            'description': 'Настройки отображения галереи. Выберите вид отображения (плитка, карусель, кирпичная кладка) и возможность открытия изображений на весь экран.'
        }),
        ('Настройки FAQ (для типа "FAQ")', {
            'fields': ('faq_icon', 'faq_icon_preview', 'faq_icon_position', 'faq_background_color', 'faq_background_image', 'faq_background_image_preview', 'faq_animation', 'faq_columns'),
            'description': 'Настройки визуального оформления секции FAQ. Можно выбрать иконку для вопросов, её позицию (слева или справа), цвет фона, фоновое изображение, тип анимации при раскрытии вопросов и количество колонок (1, 2 или 3 вопроса в строке).'
        }),
        ('Филиалы для отображения', {
            'fields': ('display_branches',),
            'description': 'Выберите филиалы, которые будут отображаться на этой странице. Можно использовать для создания страницы контактов или страницы с информацией о филиалах.'
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
    
    def faq_icon_preview(self, obj):
        if obj and obj.faq_icon:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px; object-fit: contain;" />',
                obj.faq_icon.url
            )
        return "Нет иконки"
    faq_icon_preview.short_description = 'Превью иконки FAQ'
    
    def faq_background_image_preview(self, obj):
        if obj and obj.faq_background_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.faq_background_image.url
            )
        return "Нет фонового изображения"
    faq_background_image_preview.short_description = 'Превью фонового изображения FAQ'
    
    def get_inlines(self, request, obj):
        """Показываем inline формы в зависимости от типа страницы"""
        # Базовые inline формы (каталог и галерея доступны на всех страницах)
        inlines = list(self.inlines) if hasattr(self, 'inlines') else []
        
        # Блоки главной страницы только для типа 'home'
        if obj and obj.pk and obj.page_type == 'home':
            inlines.append(HomePageBlockInline)
        
        # FAQ элементы только для типа 'faq'
        if obj and obj.pk and obj.page_type == 'faq':
            inlines.append(FAQItemInline)
        
        return inlines


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'page', 'service', 'branch', 'width', 'has_own_page', 'slug', 'button_type', 'order', 'is_active', 'card_image_preview']
    list_editable = ['order', 'is_active', 'has_own_page', 'width']
    list_filter = ['page', 'service', 'branch', 'has_own_page', 'button_type', 'is_active', 'width']
    search_fields = ['title', 'description', 'slug', 'service__title', 'branch__name']
    readonly_fields = ['card_image_preview', 'page_image_preview']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'service', 'branch', 'title'),
            'description': 'Выберите услугу или филиал для автоматического заполнения данных элемента каталога. Название, описание и изображение будут автоматически взяты из выбранной услуги или филиала, но их можно переопределить вручную.'
        }),
        ('Карточка (превью в списке)', {
            'fields': ('card_image', 'card_image_preview', 'card_description', 'width', 'button_type', 'button_text', 'button_booking_form', 'button_quiz', 'button_url'),
            'description': 'Настройки отображения карточки элемента в списке каталога. Изображение, краткое описание (с форматированием), ширина карточки и настройки кнопки.'
        }),
        ('Страница элемента', {
            'fields': ('has_own_page', 'slug', 'description', 'image', 'page_image_preview', 'image_align', 'image_size', 'gallery_page'),
            'description': 'Настройки страницы элемента (отображается при открытии карточки, если включен режим "Может быть открыт как страница"). Здесь можно задать полное описание с форматированием, изображение и параметры отображения. Видео можно вставлять прямо в редактор описания через кнопку "Вставить видео". Можно выбрать страницу галереи, которая будет отображаться на странице элемента.'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def card_image_preview(self, obj):
        """Превью изображения карточки"""
        if obj and obj.card_image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain;" />',
                obj.card_image.url
            )
        elif obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain; opacity: 0.5;" title="Используется изображение страницы" />',
                obj.image.url
            )
        return "Нет изображения"
    card_image_preview.short_description = 'Превью карточки'
    
    def page_image_preview(self, obj):
        """Превью изображения страницы"""
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "Нет изображения"
    page_image_preview.short_description = 'Превью страницы'


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ['question', 'page', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['page', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'question', 'answer')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['page', 'content_type', 'order', 'is_active', 'content_preview', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['page', 'content_type', 'is_active', 'created_at']
    readonly_fields = ['content_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'content_type', 'description')
        }),
        ('Изображение', {
            'fields': ('image', 'content_preview'),
            'description': 'Загрузите изображение, если тип контента - "Изображение"'
        }),
        ('Видео', {
            'fields': ('video_file', 'video_url'),
            'description': 'Загрузите видео файл или укажите URL видео с хостинга (YouTube, Rutube, Vimeo), если тип контента - "Видео"'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def content_preview(self, obj):
        if obj and obj.content_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        elif obj and obj.content_type == 'video':
            if obj.video_file:
                return format_html(
                    '<video src="{}" style="max-width: 200px; max-height: 200px;" controls></video>',
                    obj.video_file.url
                )
            elif obj.video_url:
                return format_html(
                    '<div style="max-width: 200px; padding: 10px; background: #f0f0f0; border-radius: 4px;">'
                    '<strong>Видео URL:</strong><br/>'
                    '<a href="{}" target="_blank">{}</a>'
                    '</div>',
                    obj.video_url, obj.video_url[:50] + '...' if len(obj.video_url) > 50 else obj.video_url
                )
        return "Нет контента"
    content_preview.short_description = 'Превью'


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
    extra = 0
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
    extra = 0
    fields = ['title', 'image', 'content_page', 'url', 'parent', 'order', 'is_active', 'is_external']
    show_change_link = True


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'item_type', 'menu', 'parent', 'url', 'order', 'is_active', 'is_external', 'image_preview']
    list_editable = ['order', 'is_active', 'is_external']
    list_filter = ['menu', 'is_active', 'parent', 'item_type']
    search_fields = ['title', 'url']
    list_display_links = ['display_name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('menu', 'item_type', 'parent'),
            'description': 'Выберите тип пункта меню. "Селектор филиала" отобразит выбор филиала в меню.'
        }),
        ('Контент (для типа "Обычная ссылка")', {
            'fields': ('title', 'image', 'image_preview', 'content_page', 'url'),
            'description': 'Укажите либо текст (title), либо загрузите изображение. Выберите страницу контента или укажите URL вручную. Эти поля используются только для типа "Обычная ссылка".'
        }),
        ('Настройки', {
            'fields': ('order', 'is_active', 'is_external')
        }),
    )
    
    readonly_fields = ['image_preview']
    
    def display_name(self, obj):
        """Отображает название или информацию об изображении"""
        if obj.item_type == 'branch_selector':
            return '📍 Селектор филиала'
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


class ServiceBranchInline(admin.TabularInline):
    """Inline для управления услугами в филиалах"""
    model = ServiceBranch
    extra = 0
    fields = ['branch', 'price', 'price_with_abonement', 'is_available', 'order', 'crm_item_id']
    readonly_fields = []
    show_change_link = True
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Если услуга новая, не показываем inline
        if obj is None:
            formset.extra = 0
        return formset


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'price_with_abonement', 'has_own_page', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'has_own_page', 'created_at']
    search_fields = ['title', 'description', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ServiceBranchInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'short_description')
        }),
        ('Цены (базовые)', {
            'fields': ('price', 'price_with_abonement', 'duration'),
            'description': 'Базовые цены услуги. Если для филиала не указана индивидуальная цена, будет использована базовая.'
        }),
        ('Изображение', {
            'fields': ('image', 'image_align', 'image_size')
        }),
        ('Настройки страницы', {
            'fields': ('has_own_page', 'show_booking_button', 'booking_form')
        }),
        ('Настройки', {
            'fields': ('order', 'is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['add_to_all_branches', 'remove_from_all_branches']
    
    def save_formset(self, request, form, formset, change):
        """Переопределяем для передачи пользователя при сохранении inline"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ServiceBranch) and change:
                instance.save(changed_by=request.user)
            else:
                instance.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()
    
    def add_to_all_branches(self, request, queryset):
        """Добавить выбранные услуги во все активные филиалы"""
        branches = Branch.objects.filter(is_active=True)
        count = 0
        for service in queryset:
            for branch in branches:
                ServiceBranch.objects.get_or_create(
                    service=service,
                    branch=branch,
                    defaults={
                        'is_available': True,
                        'order': service.order
                    }
                )
                count += 1
        self.message_user(request, f'Добавлено {count} связей услуг с филиалами.')
    add_to_all_branches.short_description = 'Добавить во все активные филиалы'
    
    def remove_from_all_branches(self, request, queryset):
        """Удалить выбранные услуги из всех филиалов"""
        count = ServiceBranch.objects.filter(service__in=queryset).delete()[0]
        self.message_user(request, f'Удалено {count} связей услуг с филиалами.')
    remove_from_all_branches.short_description = 'Удалить из всех филиалов'


@admin.register(ServiceBranch)
class ServiceBranchAdmin(admin.ModelAdmin):
    list_display = ['service', 'branch', 'get_final_price', 'get_final_price_with_abonement', 'is_available', 'order', 'crm_item_id']
    list_editable = ['is_available', 'order']
    list_filter = ['is_available', 'branch', 'service', 'created_at']
    search_fields = ['service__title', 'branch__name', 'crm_item_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('service', 'branch')
        }),
        ('Цены', {
            'fields': ('price', 'price_with_abonement'),
            'description': 'Если не указаны, используются базовые цены из услуги'
        }),
        ('Интеграция с CRM', {
            'fields': ('crm_item_id', 'crm_item_data')
        }),
        ('Настройки', {
            'fields': ('is_available', 'order', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Переопределяем save для передачи пользователя в ServiceBranch.save()"""
        if change:
            obj.save(changed_by=request.user)
        else:
            obj.save()
        super().save_model(request, obj, form, change)
    
    def get_final_price(self, obj):
        """Показывает финальную цену (из ServiceBranch или Service)"""
        price = obj.get_final_price()
        return f'{price} ₽' if price else '-'
    get_final_price.short_description = 'Цена'
    
    def get_final_price_with_abonement(self, obj):
        """Показывает финальную цену по абонементу"""
        price = obj.get_final_price_with_abonement()
        return f'{price} ₽' if price else '-'
    get_final_price_with_abonement.short_description = 'Цена по абонементу'


@admin.register(ServiceBranchPriceHistory)
class ServiceBranchPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['service_branch', 'price', 'price_with_abonement', 'changed_at', 'changed_by']
    list_filter = ['changed_at', 'service_branch__branch', 'service_branch__service']
    search_fields = ['service_branch__service__title', 'service_branch__branch__name', 'notes']
    readonly_fields = ['service_branch', 'price', 'price_with_abonement', 'changed_at', 'changed_by', 'notes']
    date_hierarchy = 'changed_at'
    
    fieldsets = (
        ('Информация об изменении', {
            'fields': ('service_branch', 'price', 'price_with_abonement', 'changed_at', 'changed_by', 'notes')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # История создается автоматически
    
    def has_delete_permission(self, request, obj=None):
        return False  # Историю нельзя удалять


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
            elif model in [Branch, Service, ServiceBranch, ServiceBranchPriceHistory]:
                category = 'Филиалы и услуги'
            elif model in [ContentPage, CatalogItem, GalleryImage, HomePageBlock, FAQItem, WelcomeBanner]:
                category = 'Контент'
            elif model in [HeaderSettings, Menu, MenuItem, FooterSettings, SocialNetwork]:
                category = 'Шапка и Подвал'
            elif model in [HeroSettings, SiteSettings]:
                category = 'Настройки сайта'
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
    
    # Определяем порядок категорий (не по алфавиту, а логически)
    category_order = {
        'Контакты': 1,
        'Филиалы и услуги': 2,
        'Контент': 3,
        'Шапка и Подвал': 4,
        'Настройки сайта': 5,
        'Политики': 6,
    }
    
    # Сортируем приложения по заданному порядку
    app_list = sorted(app_dict.values(), key=lambda x: category_order.get(x['name'], 999))
    
    # Сортируем модели внутри каждого приложения
    for app in app_list:
        if app['name'] == 'Контент':
            # Кастомный порядок для раздела "Контент"
            content_order = {
                'Страницы контента': 1,
                'Блоки главной страницы': 2,
                'Элементы каталога': 3,
                'Элементы галереи': 4,
                'Элементы FAQ': 5,
                'Приветственные баннеры': 6,
            }
            app['models'].sort(key=lambda x: content_order.get(x['name'], 999))
        elif app['name'] == 'Филиалы и услуги':
            # Порядок для раздела "Филиалы и услуги"
            services_order = {
                'Филиалы': 1,
                'Услуги': 2,
                'Услуги в филиалах': 3,
                'История изменений цен': 4,
            }
            app['models'].sort(key=lambda x: services_order.get(x['name'], 999))
        elif app['name'] == 'Шапка и Подвал':
            # Порядок для раздела "Шапка и Подвал"
            header_footer_order = {
                'Меню': 1,
                'Пункты меню': 2,
                'Настройки шапки': 3,
                'Настройки подвала': 4,
                'Социальные сети': 5,
            }
            app['models'].sort(key=lambda x: header_footer_order.get(x['name'], 999))
        elif app['name'] == 'Настройки сайта':
            # Порядок для раздела "Настройки сайта"
            settings_order = {
                'Настройки Hero': 1,
                'Настройки цвета сайта': 2,
            }
            app['models'].sort(key=lambda x: settings_order.get(x['name'], 999))
        else:
            # Для остальных разделов сортируем по имени
            app['models'].sort(key=lambda x: x['name'])
    
    return app_list

# Переопределяем метод get_app_list
admin.site.get_app_list = types.MethodType(custom_get_app_list, admin.site)
