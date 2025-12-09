from django.urls import path
from .views import webhook

app_name = 'telegram'

urlpatterns = [
    path('webhook/', webhook, name='webhook'),
]

