from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.utils import timezone
from .models import (
    Contact, Branch,
    MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings,
    ContentPage, WelcomeBanner, CatalogItem, Service
)
from .serializers import (
    ContactSerializer, BranchSerializer,
    MenuItemSerializer, HeaderSettingsSerializer, HeroSettingsSerializer,
    FooterSettingsSerializer, PrivacyPolicySerializer, SiteSettingsSerializer,
    ContentPageSerializer, WelcomeBannerSerializer, CatalogItemSerializer, ServiceSerializer
)


class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.filter(is_active=True)
    serializer_class = ContactSerializer


class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для филиалов"""
    queryset = Branch.objects.filter(is_active=True).select_related('content_page').order_by('order', 'name')
    serializer_class = BranchSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_active=True, parent__isnull=True).order_by('order')
    serializer_class = MenuItemSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class HeaderSettingsView(APIView):
    def get(self, request):
        settings = HeaderSettings.objects.first()
        if not settings:
            settings = HeaderSettings.objects.create()
        serializer = HeaderSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)


class HeroSettingsView(APIView):
    def get(self, request):
        settings = HeroSettings.objects.first()
        if not settings:
            settings = HeroSettings.objects.create()
        serializer = HeroSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)


class FooterSettingsView(APIView):
    def get(self, request):
        settings = FooterSettings.objects.first()
        if not settings:
            settings = FooterSettings.objects.create()
        serializer = FooterSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)


class PrivacyPolicyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для политик (конфиденциальности, авторских прав и т.д.)"""
    queryset = PrivacyPolicy.objects.filter(is_active=True, is_published=True).order_by('order', 'title')
    serializer_class = PrivacyPolicySerializer
    lookup_field = 'slug'
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        """Получить политику по slug"""
        try:
            policy = self.queryset.get(slug=slug)
            serializer = self.get_serializer(policy)
            return Response(serializer.data)
        except PrivacyPolicy.DoesNotExist:
            return Response({'error': 'Политика не найдена'}, status=status.HTTP_404_NOT_FOUND)


class SiteSettingsView(APIView):
    def get(self, request):
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        serializer = SiteSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)


class ContentPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentPage.objects.filter(is_active=True).prefetch_related(
        'catalog_items',
        'gallery_images',
        'home_blocks__content_page__catalog_items',
        'home_blocks__content_page__gallery_images',
        'home_blocks__content_page__faq_items',
        'home_blocks__content_page__selected_catalog_page__catalog_items',
        'home_blocks__content_page__selected_gallery_page__gallery_images',
        'home_blocks__content_page__selected_catalog_page',
        'home_blocks__content_page__selected_gallery_page',
        'faq_items',
        'branches',
        'display_branches',
        'display_services__service_branches__branch',
        'selected_catalog_page__catalog_items',
        'selected_gallery_page__gallery_images'
    ).select_related(
        'selected_catalog_page',
        'selected_gallery_page'
    )
    serializer_class = ContentPageSerializer
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f'Запрос страницы по slug: {slug}')
            # Используем базовый queryset без фильтра is_active для отладки
            # Но все равно фильтруем только активные страницы
            page = ContentPage.objects.filter(is_active=True).prefetch_related(
                'catalog_items',
                'gallery_images',
                'home_blocks__content_page__catalog_items',
                'home_blocks__content_page__gallery_images',
                'home_blocks__content_page__faq_items',
                'home_blocks__content_page__selected_catalog_page__catalog_items',
                'home_blocks__content_page__selected_gallery_page__gallery_images',
                'home_blocks__content_page__selected_catalog_page',
                'home_blocks__content_page__selected_gallery_page',
                'faq_items',
                'branches',
                'display_branches',
                'display_services__service_branches__branch',
                'selected_catalog_page__catalog_items',
                'selected_gallery_page__gallery_images'
            ).select_related(
                'selected_catalog_page',
                'selected_gallery_page'
            ).get(slug=slug)
            
            # Логирование для отладки
            logger.info(f'Loading page by slug: {slug}, page_type: {page.page_type}, is_active: {page.is_active}')
            all_blocks = page.home_blocks.all()
            active_blocks = page.home_blocks.filter(is_active=True)
            logger.info(f'Home blocks - total: {all_blocks.count()}, active: {active_blocks.count()}')
            
            for block in active_blocks:
                logger.info(f'  Block {block.id}: is_active={block.is_active}, content_page={block.content_page_id}, content_page_type={block.content_page.page_type if block.content_page else None}')
                if block.content_page and block.content_page.page_type == 'faq':
                    faq_count = block.content_page.faq_items.filter(is_active=True).count()
                    logger.info(f'    FAQ items active: {faq_count}')
            
            serializer = self.get_serializer(page)
            data = serializer.data
            logger.info(f'Serialized data - home_blocks count: {len(data.get("home_blocks", []))}')
            return Response(data)
        except ContentPage.DoesNotExist:
            logger.warning(f'Page not found by slug: {slug}')
            return Response({'error': 'Страница не найдена'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error loading page by slug {slug}: {e}', exc_info=True)
            return Response({'error': f'Ошибка загрузки страницы: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='home')
    def home_page(self, request):
        """Получить главную страницу по типу 'home'"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            page = ContentPage.objects.filter(
                is_active=True,
                page_type='home'
            ).prefetch_related(
                'catalog_items',
                'gallery_images',
                'home_blocks__content_page__catalog_items',
                'home_blocks__content_page__gallery_images',
                'home_blocks__content_page__faq_items',
                'home_blocks__content_page__selected_catalog_page__catalog_items',
                'home_blocks__content_page__selected_gallery_page__gallery_images',
                'home_blocks__content_page__selected_catalog_page',
                'home_blocks__content_page__selected_gallery_page',
                'faq_items',
                'branches',
                'display_branches',
                'display_services__service_branches__branch',
                'selected_catalog_page__catalog_items',
                'selected_gallery_page__gallery_images'
            ).select_related(
                'selected_catalog_page',
                'selected_gallery_page'
            ).first()
            
            if not page:
                logger.warning('Home page not found')
                return Response({'error': 'Главная страница не найдена'}, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f'Loading home page: id={page.id}, slug={page.slug}, is_active={page.is_active}')
            all_blocks = page.home_blocks.all()
            active_blocks = page.home_blocks.filter(is_active=True)
            logger.info(f'Home blocks - total: {all_blocks.count()}, active: {active_blocks.count()}')
            
            serializer = self.get_serializer(page)
            data = serializer.data
            logger.info(f'Serialized data - home_blocks count: {len(data.get("home_blocks", []))}')
            return Response(data)
        except Exception as e:
            logger.error(f'Error loading home page: {e}', exc_info=True)
            return Response({'error': f'Ошибка загрузки главной страницы: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WelcomeBannerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WelcomeBannerSerializer

    def get_queryset(self):
        now = timezone.now()
        queryset = WelcomeBanner.objects.filter(is_active=True).order_by('order')
        queryset = queryset.filter(
            models.Q(start_at__isnull=True) | models.Q(start_at__lte=now),
            models.Q(end_at__isnull=True) | models.Q(end_at__gte=now),
        )
        queryset = queryset.prefetch_related('cards')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CatalogItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для элементов каталога"""
    queryset = CatalogItem.objects.filter(is_active=True, has_own_page=True)
    serializer_class = CatalogItemSerializer
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        """Получить элемент каталога по slug"""
        try:
            item = self.queryset.get(slug=slug)
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        except CatalogItem.DoesNotExist:
            return Response({'error': 'Элемент каталога не найден'}, status=status.HTTP_404_NOT_FOUND)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для услуг"""
    queryset = Service.objects.filter(is_active=True, has_own_page=True)
    serializer_class = ServiceSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Фильтруем услуги по филиалу, если указан branch_id"""
        queryset = super().get_queryset()
        branch_id = self.request.query_params.get('branch_id', None)
        
        if branch_id:
            try:
                branch_id = int(branch_id)
                # Фильтруем услуги, которые доступны в указанном филиале
                queryset = queryset.filter(
                    service_branches__branch_id=branch_id,
                    service_branches__is_available=True,
                    service_branches__branch__is_active=True
                ).distinct()
            except (ValueError, TypeError):
                pass  # Игнорируем невалидный branch_id
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        """Получить услугу по slug"""
        try:
            service = self.get_queryset().get(slug=slug)
            serializer = self.get_serializer(service)
            return Response(serializer.data)
        except Service.DoesNotExist:
            return Response({'error': 'Услуга не найдена'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='by-branch/(?P<branch_id>[^/.]+)')
    def by_branch(self, request, branch_id=None):
        """Получить услуги по филиалу"""
        try:
            branch_id = int(branch_id)
            services = self.get_queryset().filter(
                service_branches__branch_id=branch_id,
                service_branches__is_available=True,
                service_branches__branch__is_active=True
            ).distinct()
            serializer = self.get_serializer(services, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response({'error': 'Неверный ID филиала'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
