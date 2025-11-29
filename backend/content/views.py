from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Contact,
    MenuItem, HeaderSettings, HeroSettings, FooterSettings, PrivacyPolicy, SiteSettings,
    ContentPage
)
from .serializers import (
    ContactSerializer,
    MenuItemSerializer, HeaderSettingsSerializer, HeroSettingsSerializer,
    FooterSettingsSerializer, PrivacyPolicySerializer, SiteSettingsSerializer,
    ContentPageSerializer
)


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


class ContentPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentPage.objects.filter(is_active=True)
    serializer_class = ContentPageSerializer
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        try:
            page = self.queryset.get(slug=slug)
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        except ContentPage.DoesNotExist:
            return Response({'error': 'Страница не найдена'}, status=status.HTTP_404_NOT_FOUND)
