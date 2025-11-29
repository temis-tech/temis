from rest_framework import serializers
from django.conf import settings
from .models import (
    Branch, Service, Specialist, Review, Promotion, Article, Contact,
    MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings
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
        # Используем переменную окружения или дефолтный домен
        api_domain = getattr(settings, 'API_DOMAIN', 'api.rainbow-say.estenomada.es')
        protocol = 'https' if not settings.DEBUG else 'http'
        # Заменяем localhost на правильный домен
        image_url = image_url.replace('http://localhost:8001', f'{protocol}://{api_domain}')
        image_url = image_url.replace('http://127.0.0.1:8001', f'{protocol}://{api_domain}')
        return image_url
    
    # Если есть request, используем build_absolute_uri
    if request:
        return request.build_absolute_uri(image_url)
    
    # Если URL уже абсолютный, возвращаем как есть
    if image_url.startswith('http://') or image_url.startswith('https://'):
        return image_url
    
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
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'description', 'short_description', 'price', 
                 'price_with_abonement', 'duration', 'image', 'order', 
                 'show_booking_button', 'booking_form_id', 'booking_form_title']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))


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
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'image', 'url', 'parent', 'order', 'is_external', 'children']
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order')
        return MenuItemSerializer(children, many=True).data
    
    def get_image(self, obj):
        """Возвращает полный URL изображения"""
        return get_image_url(obj.image, self.context.get('request'))


class HeaderSettingsSerializer(serializers.ModelSerializer):
    logo_image = serializers.SerializerMethodField()
    
    class Meta:
        model = HeaderSettings
        fields = ['logo_text', 'logo_image', 'logo_url', 'logo_height', 'header_height', 
                 'show_menu', 'show_phone', 'phone_text']
    
    def get_logo_image(self, obj):
        return get_image_url(obj.logo_image, self.context.get('request'))


class HeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    button_quiz_slug = serializers.SerializerMethodField()
    button_booking_form_id = serializers.SerializerMethodField()
    
    class Meta:
        model = HeroSettings
        fields = ['title', 'subtitle', 'button_text', 'button_url', 'button_type', 'button_quiz_slug', 
                  'button_booking_form_id', 'background_image', 'background_color',
                  'image_position', 'image_vertical_align', 'image_size', 'image_scale', 'show_overlay', 
                  'overlay_opacity', 'text_align', 'is_active']
    
    def get_background_image(self, obj):
        """Возвращает полный URL фонового изображения"""
        return get_image_url(obj.background_image, self.context.get('request'))
    
    def get_button_quiz_slug(self, obj):
        """Возвращает slug квиза для кнопки, если он активен"""
        if obj.button_quiz and obj.button_quiz.is_active and obj.button_quiz.slug:
            return obj.button_quiz.slug
        return None
    
    def get_button_booking_form_id(self, obj):
        """Возвращает ID формы записи для кнопки, если она активна"""
        if obj.button_booking_form and obj.button_booking_form.is_active:
            return obj.button_booking_form.id
        return None


class FooterSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterSettings
        fields = ['copyright_text', 'show_contacts', 'show_navigation', 'show_social', 'additional_text']


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['title', 'content', 'is_published', 'updated_at']


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['primary_color', 'gradient_start', 'gradient_end', 'secondary_color', 
                 'text_color', 'background_color']

