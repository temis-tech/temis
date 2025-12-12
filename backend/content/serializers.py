from rest_framework import serializers
from django.conf import settings
from config.constants import get_api_domain, get_protocol, get_media_base_url, MEDIA_PATH
from .models import (
    Branch, Service, Specialist, Review, Promotion, Article, Contact,
    Menu, MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings,
    ContentPage, CatalogItem, GalleryImage, HomePageBlock,
    WelcomeBanner, WelcomeBannerCard, SocialNetwork
)


def get_image_url(image_field, request=None):
    """Возвращает полный URL изображения, заменяя localhost на правильный домен"""
    if not image_field:
        return None
    
    image_url = image_field.url
    
    # Исправляем дублирование путей (например, logo/logo/logo/... -> logo/logo/)
    # Это исправляет уже сохраненные в БД неправильные пути
    # Правильный путь: /media/logo/logo/filename.jpg (два logo)
    import re
    # Находим последовательные повторения одного сегмента (3+ раза) и заменяем на 2
    # Например: /media/logo/logo/logo/logo/logo/logo/logo/file.jpg -> /media/logo/logo/file.jpg
    pattern = r'/([^/]+)(?:/\1){2,}/'
    def replace_func(match):
        segment = match.group(1)
        return f'/{segment}/{segment}/'
    image_url = re.sub(pattern, replace_func, image_url)
    
    # Если URL содержит localhost, заменяем на правильный домен
    if 'localhost' in image_url or '127.0.0.1' in image_url:
        api_domain = get_api_domain()
        protocol = get_protocol()
        # Заменяем localhost на правильный домен
        image_url = image_url.replace('http://localhost:8001', f'{protocol}://{api_domain}')
        image_url = image_url.replace('http://127.0.0.1:8001', f'{protocol}://{api_domain}')
        return image_url
    
    # Если URL уже абсолютный, проверяем и исправляем домен
    if image_url.startswith('http://') or image_url.startswith('https://'):
        api_domain = get_api_domain()
        protocol = get_protocol()
        
        # Если URL уже содержит правильный API домен, возвращаем как есть
        if api_domain in image_url:
            return image_url
        
        # Заменяем неправильные домены на правильный API домен
        import re
        # Заменяем dev.logoped-spb.pro на api.dev.logoped-spb.pro
        image_url = re.sub(
            r'https?://dev\.logoped-spb\.pro(' + MEDIA_PATH + r'/.*)',
            f'{protocol}://{api_domain}\\1',
            image_url
        )
        # Заменяем любые другие домены с /media/ на правильный API домен
        image_url = re.sub(
            r'https?://[^/]+(' + MEDIA_PATH + r'/.*)',
            f'{protocol}://{api_domain}\\1',
            image_url
        )
        return image_url
    
    # Если есть request, формируем абсолютный URL используя правильный API домен
    if request:
        api_domain = get_api_domain()
        protocol = get_protocol()
        
        # Если image_url уже абсолютный, исправляем домен
        if image_url.startswith('http://') or image_url.startswith('https://'):
            import re
            # Если URL уже содержит правильный API домен, возвращаем как есть
            if api_domain in image_url:
                return image_url
            
            # Заменяем dev.logoped-spb.pro на api.dev.logoped-spb.pro
            image_url = re.sub(
                r'https?://dev\.logoped-spb\.pro(' + MEDIA_PATH + r'/.*)',
                f'{protocol}://{api_domain}\\1',
                image_url
            )
            # Заменяем любые другие домены с /media/ на правильный API домен
            image_url = re.sub(
                r'https?://[^/]+(' + MEDIA_PATH + r'/.*)',
                f'{protocol}://{api_domain}\\1',
                image_url
            )
            return image_url
        
        # Если image_url относительный, формируем абсолютный URL с правильным доменом
        # Убираем ведущий слэш если есть
        path = image_url.lstrip('/')
        return f'{protocol}://{api_domain}/{path}'
    
    # Иначе возвращаем относительный путь (будет обработан на фронтенде)
    return image_url


class BranchSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'metro', 'phone', 'image', 'order']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))


class ServiceSerializer(serializers.ModelSerializer):
    booking_form_id = serializers.IntegerField(source='booking_form.id', read_only=True, allow_null=True)
    booking_form_title = serializers.CharField(source='booking_form.title', read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'description', 'short_description', 'price', 
                 'price_with_abonement', 'duration', 'image', 'image_align', 'image_size', 'has_own_page', 'url', 'order', 
                 'show_booking_button', 'booking_form_id', 'booking_form_title']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_url(self, obj):
        """Возвращает URL страницы услуги, если она может быть открыта как страница"""
        return obj.get_absolute_url()


class SpecialistSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Specialist
        fields = ['id', 'name', 'position', 'bio', 'photo', 'branch', 'branch_name', 'order']
    
    def get_photo(self, obj):
        return get_image_url(obj.photo, self.context.get('request'))


class ReviewSerializer(serializers.ModelSerializer):
    author_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'author_name', 'author_photo', 'text', 'rating', 'order', 'created_at']
    
    def get_author_photo(self, obj):
        return get_image_url(obj.author_photo, self.context.get('request'))


class PromotionSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'slug', 'description', 'image', 'start_date', 'end_date', 'order', 'created_at']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))


class ArticleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'short_description', 'image', 
                 'views_count', 'created_at', 'updated_at']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'phone', 'phone_secondary', 'inn', 'email']


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'image', 'url', 'content_page', 'parent', 'order', 'is_external', 'children']
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order')
        return MenuItemSerializer(children, many=True, context=self.context).data
    
    def get_image(self, obj):
        """Возвращает полный URL изображения"""
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_url(self, obj):
        """Возвращает URL из content_page или из поля url"""
        if obj.content_page:
            return obj.content_page.get_absolute_url()
        return obj.url or '/'


class MenuSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = ['id', 'name', 'description', 'items']
    
    def get_items(self, obj):
        items = obj.items.filter(is_active=True, parent__isnull=True).order_by('order')
        return MenuItemSerializer(items, many=True, context=self.context).data


class HeaderSettingsSerializer(serializers.ModelSerializer):
    logo_image = serializers.SerializerMethodField()
    menu = serializers.SerializerMethodField()
    
    class Meta:
        model = HeaderSettings
        fields = ['logo_text', 'logo_image', 'logo_url', 'logo_height', 'header_height', 
                 'show_menu', 'menu', 'show_phone', 'phone_text']
    
    def get_logo_image(self, obj):
        return get_image_url(obj.logo_image, self.context.get('request'))
    
    def get_menu(self, obj):
        """Возвращает меню, если оно выбрано, иначе возвращает меню по умолчанию"""
        if obj.menu:
            return MenuSerializer(obj.menu, context=self.context).data
        
        # Если меню не выбрано, возвращаем первое активное меню или меню без привязки
        default_menu = Menu.objects.filter(is_active=True).first()
        if default_menu:
            return MenuSerializer(default_menu, context=self.context).data
        
        # Если нет меню, возвращаем пункты меню без привязки к меню (для обратной совместимости)
        items = MenuItem.objects.filter(is_active=True, parent__isnull=True, menu__isnull=True).order_by('order')
        return {
            'id': None,
            'name': 'Меню по умолчанию',
            'description': '',
            'items': MenuItemSerializer(items, many=True, context=self.context).data
        }


class HeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    button_quiz_slug = serializers.SerializerMethodField()
    button_booking_form_id = serializers.SerializerMethodField()
    
    class Meta:
        model = HeroSettings
        fields = ['title', 'subtitle', 'button_text', 'button_url', 'button_type', 'button_quiz_slug', 
                  'button_booking_form_id', 'background_image', 'background_color',
                  'image_position', 'image_vertical_align', 'image_size', 'image_scale', 'show_overlay', 
                  'overlay_opacity', 'text_align', 'content_width', 'content_width_custom', 'is_active']
    
    def get_background_image(self, obj):
        """Возвращает полный URL фонового изображения"""
        return get_image_url(obj.background_image, self.context.get('request'))
    
    def get_button_quiz_slug(self, obj):
        """Возвращает slug анкеты для кнопки, если она активна"""
        if obj.button_quiz and obj.button_quiz.is_active and obj.button_quiz.slug:
            return obj.button_quiz.slug
        return None
    
    def get_button_booking_form_id(self, obj):
        """Возвращает ID формы записи для кнопки, если она активна"""
        if obj.button_booking_form and obj.button_booking_form.is_active:
            return obj.button_booking_form.id
        return None


class SocialNetworkSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialNetwork
        fields = ['id', 'name', 'network_type', 'url', 'icon', 'order']
    
    def get_icon(self, obj):
        return get_image_url(obj.icon, self.context.get('request'))


class FooterSettingsSerializer(serializers.ModelSerializer):
    menu = serializers.SerializerMethodField()
    social_networks = serializers.SerializerMethodField()
    
    class Meta:
        model = FooterSettings
        fields = ['copyright_text', 'show_contacts', 'show_navigation', 'show_social', 'additional_text', 'menu', 'social_networks']
    
    def get_social_networks(self, obj):
        """Возвращает список активных соцсетей"""
        if obj.show_social:
            networks = SocialNetwork.objects.filter(is_active=True).order_by('order')
            return SocialNetworkSerializer(networks, many=True, context=self.context).data
        return []
    
    def get_menu(self, obj):
        """Возвращает меню для футера, если оно выбрано"""
        if hasattr(obj, 'menu') and obj.menu:
            return MenuSerializer(obj.menu, context=self.context).data
        # Если меню не выбрано, возвращаем первое активное меню
        default_menu = Menu.objects.filter(is_active=True).first()
        if default_menu:
            return MenuSerializer(default_menu, context=self.context).data
        # Если нет меню, возвращаем пункты меню без привязки
        items = MenuItem.objects.filter(is_active=True, parent__isnull=True, menu__isnull=True).order_by('order')
        return {
            'id': None,
            'name': 'Меню по умолчанию',
            'description': '',
            'items': MenuItemSerializer(items, many=True, context=self.context).data
        }


class PrivacyPolicySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivacyPolicy
        fields = ['id', 'title', 'slug', 'content', 'order', 'is_published', 'is_active', 'url', 'created_at', 'updated_at']
    
    def get_url(self, obj):
        """Возвращает URL страницы политики"""
        return obj.get_absolute_url()


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['primary_color', 'gradient_start', 'gradient_end', 'secondary_color', 
                 'text_color', 'background_color']


class CatalogItemSerializer(serializers.ModelSerializer):
    card_image = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    button_booking_form_id = serializers.SerializerMethodField()
    button_quiz_slug = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = CatalogItem
        fields = ['id', 'title', 'description', 'card_image', 'image', 'image_align', 'image_size', 'has_own_page', 'slug', 'url', 'width',
                 'button_type', 'button_text', 'button_booking_form_id', 'button_quiz_slug', 
                 'button_url', 'order']
    
    def get_card_image(self, obj):
        """Возвращает изображение для карточки (превью)"""
        # Если есть card_image, используем его, иначе используем image
        image_field = obj.card_image if obj.card_image else obj.image
        return get_image_url(image_field, self.context.get('request'))
    
    def get_image(self, obj):
        """Возвращает изображение для страницы"""
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_button_booking_form_id(self, obj):
        """Возвращает ID формы записи, если она активна"""
        if obj.button_booking_form and obj.button_booking_form.is_active:
            return obj.button_booking_form.id
        return None
    
    def get_button_quiz_slug(self, obj):
        """Возвращает slug анкеты, если она активна"""
        if obj.button_quiz and obj.button_quiz.is_active and obj.button_quiz.slug:
            return obj.button_quiz.slug
        return None
    
    def get_url(self, obj):
        """Возвращает URL страницы элемента каталога, если он может быть открыт как страница"""
        return obj.get_absolute_url()


class GalleryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'description', 'order']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))


class HomePageBlockSerializer(serializers.ModelSerializer):
    content_page_data = serializers.SerializerMethodField()
    
    class Meta:
        model = HomePageBlock
        fields = ['id', 'content_page', 'title', 'show_title', 'title_tag', 'title_align', 
                 'title_size', 'title_color', 'title_bold', 'title_italic', 'title_custom_css',
                 'order', 'is_active', 'content_page_data']
    
    def get_content_page_data(self, obj):
        """Возвращает данные страницы контента"""
        if obj.content_page:
            # Используем упрощенный сериализатор, чтобы избежать рекурсии
            # Если страница типа 'home', не сериализуем её home_blocks
            if obj.content_page.page_type == 'home':
                # Для страниц типа 'home' возвращаем только базовую информацию
                return {
                    'id': obj.content_page.id,
                    'title': obj.content_page.title,
                    'slug': obj.content_page.slug,
                    'page_type': obj.content_page.page_type,
                    'description': obj.content_page.description,
                    'is_active': obj.content_page.is_active,
                    'home_blocks': []  # Не сериализуем вложенные блоки, чтобы избежать рекурсии
                }
            # Для других типов страниц используем полный сериализатор
            serializer = ContentPageSerializer(obj.content_page, context=self.context)
            return serializer.data


class WelcomeBannerCardSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    button_booking_form_id = serializers.SerializerMethodField()
    button_quiz_slug = serializers.SerializerMethodField()

    class Meta:
        model = WelcomeBannerCard
        fields = [
            'id', 'title', 'description', 'image', 'button_type', 'button_text',
            'button_url', 'button_booking_form_id', 'button_quiz_slug', 'order', 'is_active'
        ]

    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))

    def get_button_booking_form_id(self, obj):
        if obj.button_booking_form and obj.button_booking_form.is_active:
            return obj.button_booking_form.id
        return None

    def get_button_quiz_slug(self, obj):
        if obj.button_quiz and obj.button_quiz.is_active and obj.button_quiz.slug:
            return obj.button_quiz.slug
        return None


class WelcomeBannerSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField()

    class Meta:
        model = WelcomeBanner
        fields = [
            'id', 'title', 'subtitle', 'background_color', 'text_color',
            'content_width', 'display_type', 'blur_background', 'start_at', 'end_at', 'cards'
        ]

    def get_cards(self, obj):
        cards = obj.cards.filter(is_active=True).order_by('order')
        return WelcomeBannerCardSerializer(cards, many=True, context=self.context).data


class ContentPageSerializer(serializers.ModelSerializer):
    catalog_items = serializers.SerializerMethodField()
    gallery_images = serializers.SerializerMethodField()
    home_blocks = serializers.SerializerMethodField()
    
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentPage
        fields = ['id', 'title', 'slug', 'page_type', 'description', 'image', 'image_align', 'image_size', 'show_title', 'is_active', 'catalog_items',
                 'gallery_images', 'home_blocks']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_catalog_items(self, obj):
        if obj.page_type == 'catalog':
            items = obj.catalog_items.filter(is_active=True).order_by('order')
            return CatalogItemSerializer(items, many=True, context=self.context).data
        return []
    
    def get_gallery_images(self, obj):
        if obj.page_type == 'gallery':
            images = obj.gallery_images.filter(is_active=True).order_by('order')
            return GalleryImageSerializer(images, many=True, context=self.context).data
        return []
    
    def get_home_blocks(self, obj):
        if obj.page_type == 'home':
            blocks = obj.home_blocks.filter(is_active=True).order_by('order')
            # Используем упрощенный сериализатор для блоков, чтобы избежать глубокой рекурсии
            return HomePageBlockSerializer(blocks, many=True, context=self.context).data
        return []

