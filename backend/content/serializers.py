import re
from rest_framework import serializers
from django.conf import settings
from config.constants import get_api_domain, get_protocol, get_media_base_url, MEDIA_PATH
from .models import (
    Branch, Service, ServiceBranch, Specialist, Review, Promotion, Article, Contact,
    Menu, MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings,
    ContentPage, CatalogItem, GalleryImage, HomePageBlock, FAQItem,
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
        # Заменяем старые домены на api.temis.ooo
        image_url = re.sub(
            r'https?://[^/]+\.logoped-spb\.pro(' + MEDIA_PATH + r'/.*)',
            f'{protocol}://{api_domain}\\1',
            image_url
        )
        # Заменяем старый домен rainbow-say.estenomada.es на api.temis.ooo
        image_url = re.sub(
            r'https?://[^/]*rainbow-say[^/]*\.estenomada\.es(' + MEDIA_PATH + r'/.*)',
            f'{protocol}://{api_domain}\\1',
            image_url
        )
        # Заменяем любые другие домены с /media/ на правильный API домен (но не api.temis.ooo)
        if api_domain not in image_url:
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
            # Всегда используем HTTPS для продакшена (исправляем HTTP на HTTPS)
            if image_url.startswith('http://'):
                image_url = image_url.replace('http://', 'https://', 1)
            
            # Если URL уже содержит правильный API домен, возвращаем как есть
            if api_domain in image_url:
                return image_url
            
            # Заменяем старые домены на api.temis.ooo
            image_url = re.sub(
                r'https?://[^/]+\.logoped-spb\.pro(' + MEDIA_PATH + r'/.*)',
                f'{protocol}://{api_domain}\\1',
                image_url
            )
            # Заменяем старый домен rainbow-say.estenomada.es на api.temis.ooo
            image_url = re.sub(
                r'https?://[^/]*rainbow-say[^/]*\.estenomada\.es(' + MEDIA_PATH + r'/.*)',
                f'{protocol}://{api_domain}\\1',
                image_url
            )
            # Заменяем любые другие домены с /media/ на правильный API домен (но не api.temis.ooo)
            if api_domain not in image_url:
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
    content_page = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'metro', 'phone', 'image', 'content_page', 'order']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_content_page(self, obj):
        """Возвращает базовую информацию о странице контента филиала, если она есть"""
        if obj.content_page:
            # Возвращаем только базовую информацию, чтобы избежать циклической зависимости
            return {
                'id': obj.content_page.id,
                'title': obj.content_page.title,
                'slug': obj.content_page.slug,
                'url': obj.content_page.get_absolute_url(),
            }
        return None


class ServiceBranchSerializer(serializers.ModelSerializer):
    """Сериализатор для связи услуги с филиалом"""
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    final_price = serializers.SerializerMethodField()
    final_price_with_abonement = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceBranch
        fields = ['id', 'branch', 'branch_id', 'branch_name', 'price', 'price_with_abonement',
                 'final_price', 'final_price_with_abonement', 'is_available', 'order',
                 'crm_item_id', 'crm_item_data']
    
    def get_final_price(self, obj):
        """Возвращает финальную цену (из ServiceBranch или Service)"""
        return float(obj.get_final_price()) if obj.get_final_price() else None
    
    def get_final_price_with_abonement(self, obj):
        """Возвращает финальную цену по абонементу"""
        price = obj.get_final_price_with_abonement()
        return float(price) if price else None


class ServiceSerializer(serializers.ModelSerializer):
    booking_form_id = serializers.IntegerField(source='booking_form.id', read_only=True, allow_null=True)
    booking_form_title = serializers.CharField(source='booking_form.title', read_only=True, allow_null=True)
    image = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    service_branches = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    price_with_abonement_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'description', 'short_description', 'price', 
                 'price_is_from', 'price_with_abonement', 'price_with_abonement_is_from', 
                 'duration', 'image', 'image_align', 'image_size', 
                 'price_duration_position', 'has_own_page', 'url', 'order', 
                 'show_booking_button', 'booking_form_id', 'booking_form_title',
                 'service_branches', 'price_range', 'price_with_abonement_range']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_url(self, obj):
        """Возвращает URL страницы услуги, если она может быть открыта как страница"""
        return obj.get_absolute_url()
    
    def get_service_branches(self, obj):
        """Возвращает список филиалов, где доступна услуга"""
        branches = obj.service_branches.filter(is_available=True, branch__is_active=True).select_related('branch')
        return ServiceBranchSerializer(branches, many=True, context=self.context).data
    
    def get_price_range(self, obj):
        """Возвращает диапазон цен по всем филиалам (min-max)"""
        branches = obj.service_branches.filter(is_available=True, branch__is_active=True)
        prices = []
        
        # Добавляем базовую цену
        if obj.price:
            prices.append(float(obj.price))
        
        # Добавляем цены из филиалов
        for branch in branches:
            final_price = branch.get_final_price()
            if final_price:
                prices.append(float(final_price))
        
        if not prices:
            return None
        
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return min_price
        return {'min': min_price, 'max': max_price}
    
    def get_price_with_abonement_range(self, obj):
        """Возвращает диапазон цен по абонементу по всем филиалам (min-max)"""
        branches = obj.service_branches.filter(is_available=True, branch__is_active=True)
        prices = []
        
        # Добавляем базовую цену по абонементу
        if obj.price_with_abonement:
            prices.append(float(obj.price_with_abonement))
        
        # Добавляем цены из филиалов
        for branch in branches:
            final_price = branch.get_final_price_with_abonement()
            if final_price:
                prices.append(float(final_price))
        
        if not prices:
            return None
        
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return min_price
        return {'min': min_price, 'max': max_price}


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
        fields = ['id', 'item_type', 'title', 'image', 'url', 'content_page', 'parent', 'order', 'is_external', 'children']
    
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
        fields = ['logo_text', 'logo_image', 'logo_url', 'logo_height', 'logo_width', 'logo_mobile_scale', 'header_height', 
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
                  'overlay_opacity', 'text_align', 'content_width', 'content_width_custom', 'height', 'is_active']
    
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
    favicon = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'page_title', 'description', 'favicon', 'primary_color', 'gradient_start', 
                 'gradient_end', 'secondary_color', 'text_color', 'background_color']
    
    def get_favicon(self, obj):
        if obj.favicon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.favicon.url)
            return obj.favicon.url
        return None


class CatalogItemSerializer(serializers.ModelSerializer):
    card_image = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    button_booking_form_id = serializers.SerializerMethodField()
    button_quiz_slug = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    gallery_page = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    service_id = serializers.IntegerField(source='service.id', read_only=True, allow_null=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True, allow_null=True)
    
    class Meta:
        model = CatalogItem
        fields = ['id', 'title', 'card_description', 'description', 'card_image', 'image', 'image_align', 'image_size', 
                 'image_position', 'image_target_width', 'image_target_height', 'has_own_page', 'slug', 'url', 'width',
                 'button_type', 'button_text', 'button_booking_form_id', 'button_quiz_slug', 
                 'button_url', 'video_url', 'video_width', 'video_height', 'gallery_page', 
                 'service', 'service_id', 'branch', 'branch_id', 'order']
    
    def to_representation(self, instance):
        """Переопределяем для безопасной обработки null значений"""
        data = super().to_representation(instance)
        # Убеждаемся, что все строковые поля не null
        if data.get('title') is None:
            data['title'] = ''
        if data.get('button_text') is None:
            data['button_text'] = ''
        if data.get('button_url') is None:
            data['button_url'] = ''
        if data.get('card_description') is None:
            data['card_description'] = ''
        if data.get('description') is None:
            data['description'] = ''
        if data.get('image_position') is None:
            data['image_position'] = 'top'
        return data
    
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
    
    def get_gallery_page(self, obj):
        """Возвращает данные страницы галереи, если она выбрана"""
        if not obj.gallery_page:
            return None
        
        # Проверяем, что страница активна
        if not obj.gallery_page.is_active:
            return None
        
        try:
            # Сериализуем страницу галереи со всеми данными
            gallery_data = ContentPageSerializer(obj.gallery_page, context=self.context).data
            
            # Убеждаемся, что gallery_images присутствует и является массивом
            if 'gallery_images' not in gallery_data or not isinstance(gallery_data.get('gallery_images'), list):
                gallery_data['gallery_images'] = []
            
            # Убеждаемся, что все обязательные поля присутствуют
            if 'id' not in gallery_data or gallery_data['id'] is None:
                gallery_data['id'] = obj.gallery_page.id
            if 'title' not in gallery_data or gallery_data['title'] is None:
                gallery_data['title'] = obj.gallery_page.title or ''
            if 'is_active' not in gallery_data:
                gallery_data['is_active'] = obj.gallery_page.is_active
            if 'show_title' not in gallery_data:
                gallery_data['show_title'] = getattr(obj.gallery_page, 'show_title', True)
            if 'gallery_display_type' not in gallery_data:
                gallery_data['gallery_display_type'] = getattr(obj.gallery_page, 'gallery_display_type', 'grid')
            if 'gallery_enable_fullscreen' not in gallery_data:
                gallery_data['gallery_enable_fullscreen'] = getattr(obj.gallery_page, 'gallery_enable_fullscreen', True)
            
            return gallery_data
        except Exception as e:
            # В случае ошибки сериализации возвращаем None
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка сериализации gallery_page для CatalogItem {obj.id}: {str(e)}', exc_info=True)
            return None
    
    def get_service(self, obj):
        """Возвращает данные услуги, если она выбрана"""
        if obj.service:
            return ServiceSerializer(obj.service, context=self.context).data
        return None
    
    def get_branch(self, obj):
        """Возвращает данные филиала, если он выбран"""
        if obj.branch:
            return BranchSerializer(obj.branch, context=self.context).data
        return None


class GalleryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video_file = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GalleryImage
        fields = ['id', 'content_type', 'image', 'video_file', 'video_url', 'video_embed_url', 'description', 'order']
    
    def get_image(self, obj):
        if obj.content_type == 'image':
            return get_image_url(obj.image, self.context.get('request'))
        return None
    
    def get_video_file(self, obj):
        if obj.content_type == 'video' and obj.video_file:
            return get_image_url(obj.video_file, self.context.get('request'))
        return None
    
    def get_video_embed_url(self, obj):
        """Конвертирует URL видео в embed URL для YouTube, Rutube, Vimeo, VK"""
        if obj.content_type == 'video' and obj.video_url:
            url = obj.video_url
            
            # YouTube
            youtube_regex = r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
            youtube_match = re.search(youtube_regex, url)
            if youtube_match:
                return f'https://www.youtube.com/embed/{youtube_match.group(1)}'
            
            # Rutube
            rutube_regex = r'rutube\.ru/(?:video|play/embed)/([a-zA-Z0-9_-]+)'
            rutube_match = re.search(rutube_regex, url)
            if rutube_match:
                return f'https://rutube.ru/play/embed/{rutube_match.group(1)}'
            
            # Vimeo
            vimeo_regex = r'(?:vimeo\.com/|player\.vimeo\.com/video/)(\d+)'
            vimeo_match = re.search(vimeo_regex, url)
            if vimeo_match:
                return f'https://player.vimeo.com/video/{vimeo_match.group(1)}'
            
            # VK (ВКонтакте)
            # Формат URL: https://vk.com/...?z=video-227252503_456239169 или https://vk.com/video-227252503_456239169
            vk_regex = r'video-(\d+)_(\d+)'
            vk_match = re.search(vk_regex, url)
            if vk_match:
                owner_id = vk_match.group(1)
                video_id = vk_match.group(2)
                # VK требует hash для embed, но можно попробовать использовать упрощенный формат
                # Если hash доступен в URL, извлекаем его
                hash_match = re.search(r'hash=([a-zA-Z0-9]+)', url)
                hash_param = hash_match.group(1) if hash_match else None
                
                if hash_param:
                    return f'https://vk.com/video_ext.php?oid={owner_id}&id={video_id}&hash={hash_param}'
                else:
                    # Возвращаем формат для обработки на фронтенде (попытка встроить без hash)
                    return f'https://vk.com/video-{owner_id}_{video_id}'
            
            # Если URL уже является embed URL, возвращаем как есть
            if '/embed/' in url or '/play/embed/' in url or '/video_ext.php' in url:
                return url
            
        return None


class FAQItemSerializer(serializers.ModelSerializer):
    """Сериализатор для элементов FAQ"""
    class Meta:
        model = FAQItem
        fields = ['id', 'question', 'answer', 'order', 'is_active']


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
            # Но нужно убедиться, что мы не создаем рекурсию
            # Используем тот же контекст, чтобы избежать проблем
            try:
                serializer = ContentPageSerializer(obj.content_page, context=self.context)
                data = serializer.data
                # Убеждаемся, что для страниц в блоках мы не возвращаем home_blocks
                # чтобы избежать глубокой рекурсии
                if 'home_blocks' in data and obj.content_page.page_type != 'home':
                    # Для страниц в блоках главной страницы не возвращаем их собственные home_blocks
                    data['home_blocks'] = []
                return data
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error serializing content_page_data for block {obj.id}: {e}')
                # Возвращаем базовую информацию в случае ошибки
                return {
                    'id': obj.content_page.id,
                    'title': obj.content_page.title,
                    'slug': obj.content_page.slug,
                    'page_type': obj.content_page.page_type,
                    'description': obj.content_page.description,
                    'is_active': obj.content_page.is_active,
                }


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
    faq_items = serializers.SerializerMethodField()
    branches = serializers.SerializerMethodField()
    
    image = serializers.SerializerMethodField()
    faq_icon = serializers.SerializerMethodField()
    faq_background_image = serializers.SerializerMethodField()
    
    display_branches = serializers.SerializerMethodField()
    display_services = serializers.SerializerMethodField()
    selected_catalog_page = serializers.SerializerMethodField()
    selected_gallery_page = serializers.SerializerMethodField()
    
    # Явно указываем show_title как BooleanField для гарантии правильного типа
    # НЕ указываем default, чтобы использовать значение из модели
    show_title = serializers.BooleanField()
    
    class Meta:
        model = ContentPage
        fields = ['id', 'title', 'slug', 'page_type', 'description', 'image', 'image_align', 'image_size', 
                 'gallery_display_type', 'gallery_enable_fullscreen', 'show_title', 'show_catalog_navigator', 'is_active', 'catalog_items',
                 'gallery_images', 'home_blocks', 'faq_items', 'faq_icon', 'faq_icon_position', 
                 'faq_background_color', 'faq_background_image', 'faq_animation', 'faq_columns', 'branches', 'display_branches',
                 'display_services', 'services_show_title', 'services_title', 'services_card_style', 'selected_catalog_page', 'selected_gallery_page']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))
    
    def get_faq_icon(self, obj):
        return get_image_url(obj.faq_icon, self.context.get('request'))
    
    def get_faq_background_image(self, obj):
        return get_image_url(obj.faq_background_image, self.context.get('request'))
    
    def get_catalog_items(self, obj):
        # Каталог можно добавить на страницу любого типа
        items = obj.catalog_items.filter(is_active=True).order_by('order')
        return CatalogItemSerializer(items, many=True, context=self.context).data
    
    def get_gallery_images(self, obj):
        # Галерею можно добавить на страницу любого типа
        images = obj.gallery_images.filter(is_active=True).order_by('order')
        return GalleryImageSerializer(images, many=True, context=self.context).data
    
    def get_home_blocks(self, obj):
        if obj.page_type == 'home':
            blocks = obj.home_blocks.filter(is_active=True).order_by('order')
            # Используем упрощенный сериализатор для блоков, чтобы избежать глубокой рекурсии
            return HomePageBlockSerializer(blocks, many=True, context=self.context).data
        return []
    
    def get_faq_items(self, obj):
        if obj.page_type == 'faq':
            items = obj.faq_items.filter(is_active=True).order_by('order')
            return FAQItemSerializer(items, many=True, context=self.context).data
        return []
    
    def get_branches(self, obj):
        """Возвращает список филиалов, связанных с этой страницей (через content_page)"""
        branches = obj.branches.filter(is_active=True).order_by('order')
        return BranchSerializer(branches, many=True, context=self.context).data
    
    def get_display_branches(self, obj):
        """Возвращает список филиалов для отображения на странице (через ManyToMany)"""
        branches = obj.display_branches.filter(is_active=True).order_by('order')
        return BranchSerializer(branches, many=True, context=self.context).data
    
    def get_display_services(self, obj):
        """Возвращает список услуг для отображения на странице (через ManyToMany)"""
        services = obj.display_services.filter(is_active=True, has_own_page=True).order_by('order')
        return ServiceSerializer(services, many=True, context=self.context).data
    
    def get_selected_catalog_page(self, obj):
        """Возвращает данные выбранной страницы каталога, если она есть"""
        if obj.selected_catalog_page and obj.selected_catalog_page.is_active:
            # Используем упрощенный сериализатор, чтобы избежать рекурсии
            return {
                'id': obj.selected_catalog_page.id,
                'title': obj.selected_catalog_page.title,
                'slug': obj.selected_catalog_page.slug,
                'catalog_items': CatalogItemSerializer(
                    obj.selected_catalog_page.catalog_items.filter(is_active=True).order_by('order'),
                    many=True,
                    context=self.context
                ).data
            }
        return None
    
    def get_selected_gallery_page(self, obj):
        """Возвращает данные выбранной страницы галереи, если она есть"""
        if obj.selected_gallery_page and obj.selected_gallery_page.is_active:
            # Используем упрощенный сериализатор, чтобы избежать рекурсии
            return {
                'id': obj.selected_gallery_page.id,
                'title': obj.selected_gallery_page.title,
                'slug': obj.selected_gallery_page.slug,
                'gallery_images': GalleryImageSerializer(
                    obj.selected_gallery_page.gallery_images.filter(is_active=True).order_by('order'),
                    many=True,
                    context=self.context
                ).data,
                'gallery_display_type': obj.selected_gallery_page.gallery_display_type,
                'gallery_enable_fullscreen': obj.selected_gallery_page.gallery_enable_fullscreen
            }
        return None

