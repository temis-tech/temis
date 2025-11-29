from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from .models import (
    Branch, Service, Specialist, Review, Promotion, Article, Contact,
    MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings
)
from .serializers import (
    BranchSerializer, ServiceSerializer, SpecialistSerializer,
    ReviewSerializer, PromotionSerializer, ArticleSerializer, ContactSerializer,
    MenuItemSerializer, HeaderSettingsSerializer, HeroSettingsSerializer,
    FooterSettingsSerializer, PrivacyPolicySerializer, SiteSettingsSerializer
)


class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        try:
            service = self.queryset.get(slug=slug)
            serializer = self.get_serializer(service)
            return Response(serializer.data)
        except Service.DoesNotExist:
            return Response({'error': 'Услуга не найдена'}, status=status.HTTP_404_NOT_FOUND)


class SpecialistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialist.objects.filter(is_active=True)
    serializer_class = SpecialistSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            specialists = self.queryset.filter(branch_id=branch_id)
        else:
            specialists = self.queryset
        serializer = self.get_serializer(specialists, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.filter(is_published=True)
    serializer_class = ReviewSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PromotionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        now = timezone.now().date()
        return self.queryset.filter(
            is_active=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        try:
            promotion = self.get_queryset().get(slug=slug)
            serializer = self.get_serializer(promotion)
            return Response(serializer.data)
        except Promotion.DoesNotExist:
            return Response({'error': 'Акция не найдена'}, status=status.HTTP_404_NOT_FOUND)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        try:
            article = self.queryset.get(slug=slug)
            article.views_count += 1
            article.save(update_fields=['views_count'])
            serializer = self.get_serializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            return Response({'error': 'Статья не найдена'}, status=status.HTTP_404_NOT_FOUND)


class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.filter(is_active=True)
    serializer_class = ContactSerializer


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
        serializer = FooterSettingsSerializer(settings)
        return Response(serializer.data)


class PrivacyPolicyView(APIView):
    def get(self, request):
        policy = PrivacyPolicy.objects.first()
        if not policy:
            policy = PrivacyPolicy.objects.create()
        serializer = PrivacyPolicySerializer(policy)
        return Response(serializer.data)


class SiteSettingsView(APIView):
    def get(self, request):
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)

