from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactViewSet,
    MenuItemViewSet, HeaderSettingsView, HeroSettingsView,
    FooterSettingsView, PrivacyPolicyView, SiteSettingsView, ContentPageViewSet
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'menu', MenuItemViewSet, basename='menuitem')
router.register(r'pages', ContentPageViewSet, basename='contentpage')

urlpatterns = [
    path('', include(router.urls)),
    path('settings/header/', HeaderSettingsView.as_view(), name='header-settings'),
    path('settings/hero/', HeroSettingsView.as_view(), name='hero-settings'),
    path('settings/footer/', FooterSettingsView.as_view(), name='footer-settings'),
    path('settings/site/', SiteSettingsView.as_view(), name='site-settings'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
]

