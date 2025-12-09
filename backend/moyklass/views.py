"""
Views для работы с MoyKlass интеграцией
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
import json
from .models import MoyKlassSettings
from .client import MoyKlassClient, MoyKlassAPIError


@method_decorator(csrf_exempt, name='dispatch')
class MoyKlassWebhookView(View):
    """
    View для обработки вебхуков от MoyKlass
    
    MoyKlass может отправлять уведомления о событиях:
    - Создание/обновление ученика
    - Создание платежа
    - Создание/отмена записи
    - и т.д.
    """
    
    def post(self, request):
        """Обрабатывает POST запрос от MoyKlass"""
        settings = MoyKlassSettings.objects.first()
        
        if not settings or not settings.webhook_enabled:
            return JsonResponse({'error': 'Webhooks disabled'}, status=403)
        
        try:
            data = json.loads(request.body)
            event_type = data.get('event')
            event_data = data.get('data', {})
            
            # Обрабатываем событие
            # Здесь можно добавить логику обработки различных типов событий
            # Например:
            # if event_type == 'student.created':
            #     # Обработать создание ученика
            # elif event_type == 'payment.created':
            #     # Обработать создание платежа
            
            return JsonResponse({'status': 'ok', 'event': event_type})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request):
        """Проверка доступности вебхука (для тестирования)"""
        settings = MoyKlassSettings.objects.first()
        
        if not settings or not settings.webhook_enabled:
            return JsonResponse({'status': 'disabled'}, status=403)
        
        return JsonResponse({
            'status': 'active',
            'webhook_url': settings.webhook_url
        })


@csrf_exempt
@require_http_methods(["POST"])
def create_student_from_booking(request):
    """
    Создает ученика в MoyKlass на основе данных из формы записи
    
    Этот endpoint можно вызывать после успешной отправки формы записи
    """
    try:
        data = json.loads(request.body)
        
        settings = MoyKlassSettings.objects.first()
        if not settings or not settings.is_active:
            return JsonResponse({'error': 'MoyKlass integration is not active'}, status=403)
        
        client = MoyKlassClient(settings)
        
        # Формируем данные для создания ученика в MoyKlass
        student_data = {
            'name': data.get('name'),
            'phone': data.get('phone'),
            'email': data.get('email', ''),
            'comment': data.get('description', ''),
        }
        
        # Создаем ученика в MoyKlass
        result = client.create_student(student_data)
        
        return JsonResponse({
            'success': True,
            'moyklass_student_id': result.get('id')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except MoyKlassAPIError as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def get_source_fields(request):
    """
    Возвращает список полей источника (формы записи или анкеты) для AJAX запроса
    """
    source_type = request.GET.get('source_type')
    source_id = request.GET.get('source_id')
    
    if not source_type or not source_id:
        return JsonResponse({'error': 'Не указан тип источника или ID'}, status=400)
    
    fields = []
    
    try:
        if source_type == 'booking_form':
            from booking.models import BookingForm
            form = BookingForm.objects.get(id=source_id)
            for field in form.fields.all():
                fields.append({
                    'name': field.name,
                    'label': field.label,
                    'type': field.get_field_type_display()
                })
        elif source_type == 'quiz':
            from quizzes.models import Quiz
            quiz = Quiz.objects.get(id=source_id)
            # Добавляем базовые поля пользователя
            fields.append({
                'name': 'user_name',
                'label': 'Имя пользователя',
                'type': 'Текст'
            })
            fields.append({
                'name': 'user_phone',
                'label': 'Телефон пользователя',
                'type': 'Телефон'
            })
            fields.append({
                'name': 'user_email',
                'label': 'Email пользователя',
                'type': 'Email'
            })
            # Добавляем вопросы
            for question in quiz.questions.all():
                fields.append({
                    'name': f'question_{question.id}',
                    'label': question.text[:50],
                    'type': question.get_question_type_display()
                })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'fields': fields})
