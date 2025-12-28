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
        logger.info(f'Получен webhook от Telegram: {list(data.keys())}')
        
        # Сохраняем лог о получении webhook
        from .bot import log_sync_event
        try:
            log_sync_event(
                event_type='webhook_received',
                status='success',
                message=f'Получен webhook: {", ".join(data.keys())}',
                raw_data=data
            )
        except Exception as e:
            logger.error(f'Ошибка сохранения лога webhook: {str(e)}')
        
        # Логируем тип обновления
        if 'channel_post' in data:
            channel_post = data.get('channel_post', {})
            chat = channel_post.get('chat', {})
            message_id = channel_post.get('message_id')
            logger.info(f'Webhook: channel_post от канала {chat.get("id")} ({chat.get("username")}), message_id: {message_id}')
        elif 'edited_channel_post' in data:
            edited_post = data.get('edited_channel_post', {})
            chat = edited_post.get('chat', {})
            message_id = edited_post.get('message_id')
            logger.info(f'Webhook: edited_channel_post от канала {chat.get("id")} ({chat.get("username")}), message_id: {message_id}')
            # Сохраняем лог о получении обновленного поста
            try:
                from .bot import log_sync_event
                log_sync_event(
                    event_type='edited_channel_post',
                    status='success',
                    message=f'Получен обновленный пост из канала через webhook',
                    message_id=message_id,
                    chat_id=str(chat.get('id', '')),
                    chat_username=chat.get('username', ''),
                    raw_data=edited_post
                )
            except Exception as e:
                logger.error(f'Ошибка сохранения лога edited_channel_post: {str(e)}')
        elif 'message' in data:
            message = data.get('message', {})
            chat = message.get('chat', {})
            logger.info(f'Webhook: message от чата {chat.get("id")} ({chat.get("type")})')
        else:
            logger.debug(f'Webhook: неизвестный тип обновления: {list(data.keys())}')
        
        handle_webhook_update(data)
        return JsonResponse({'ok': True})
    except json.JSONDecodeError:
        logger.error('Ошибка парсинга JSON от Telegram webhook')
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f'Ошибка обработки webhook: {str(e)}', exc_info=True)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
