from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BranchViewSet, ServiceViewSet, SpecialistViewSet,
    ReviewViewSet, PromotionViewSet, ArticleViewSet, ContactViewSet,
    MenuItemViewSet, HeaderSettingsView, HeroSettingsView,
    FooterSettingsView, PrivacyPolicyView, SiteSettingsView
)

router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'specialists', SpecialistViewSet, basename='specialist')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'menu', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('settings/header/', HeaderSettingsView.as_view(), name='header-settings'),
    path('settings/hero/', HeroSettingsView.as_view(), name='hero-settings'),
    path('settings/footer/', FooterSettingsView.as_view(), name='footer-settings'),
    path('settings/site/', SiteSettingsView.as_view(), name='site-settings'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
]

