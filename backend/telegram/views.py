"""
Views для обработки webhook от Telegram
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .bot import handle_webhook_update

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """
    Обработчик webhook от Telegram
    """
    try:
        data = json.loads(request.body)
        handle_webhook_update(data)
        return JsonResponse({'ok': True})
    except json.JSONDecodeError:
        logger.error('Ошибка парсинга JSON от Telegram webhook')
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка обработки webhook: {str(e)}')
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
