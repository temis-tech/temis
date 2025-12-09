"""
URLs для модуля MoyKlass
"""
from django.urls import path
from . import views

app_name = 'moyklass'

urlpatterns = [
    path('webhook/', views.MoyKlassWebhookView.as_view(), name='webhook'),
    path('create-student/', views.create_student_from_booking, name='create_student'),
]

