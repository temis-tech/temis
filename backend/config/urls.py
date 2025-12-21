"""
URL configuration for temis project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from moyklass.views import get_source_fields

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/moyklass/moyklassintegration/get-source-fields/', 
         get_source_fields, name='moyklass_get_source_fields'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/content/', include('content.urls')),
    path('api/quizzes/', include('quizzes.urls')),
    path('api/booking/', include('booking.urls')),
    path('api/moyklass/', include('moyklass.urls')),
    path('api/telegram/', include('telegram.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

