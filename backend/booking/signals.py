"""
Сигналы для автоматической интеграции с Telegram
Обработка MoyKlass перенесена в tasks.py для асинхронной обработки
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookingSubmission
import logging

logger = logging.getLogger(__name__)

# Примечание: Интеграция с MoyKlass теперь обрабатывается асинхронно через tasks.py
# Сигналы оставлены только для Telegram уведомлений, которые обрабатываются быстро
