from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BookingForm, BookingSubmission, FormRule
from .serializers import BookingFormSerializer, BookingSubmissionSerializer
from .tasks import process_booking_submission_async
from content.models import Service
from quizzes.models import Quiz, QuizSubmission
import threading


class BookingFormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookingForm.objects.filter(is_active=True).prefetch_related(
        'fields',
        'rules__field',
        'rules__quiz'
    )
    serializer_class = BookingFormSerializer
    lookup_field = 'id'


class BookingSubmissionViewSet(viewsets.ModelViewSet):
    queryset = BookingSubmission.objects.all()
    serializer_class = BookingSubmissionSerializer
    
    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            form_id = request.data.get('form_id')
            service_id = request.data.get('service_id')
            source_page = request.data.get('source_page', '')
            form_data = request.data.get('data', {})
            
            # Логируем входящие данные для отладки
            logger.info(f'BookingSubmission create: form_id={form_id}, service_id={service_id}, source_page={source_page}, data={form_data}')
            
            if not form_id:
                return Response({'error': 'Не указан form_id'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                form = BookingForm.objects.get(id=form_id, is_active=True)
            except BookingForm.DoesNotExist:
                logger.error(f'BookingForm с id={form_id} не найдена или неактивна')
                return Response({'error': 'Форма не найдена'}, status=status.HTTP_404_NOT_FOUND)
            
            service = None
            if service_id:
                try:
                    service = Service.objects.get(id=service_id, is_active=True)
                except Service.DoesNotExist:
                    logger.warning(f'Service с id={service_id} не найдена или неактивна')
                    pass
            
            # Подставляем значения в скрытые поля (для всех полей, не только если есть service)
            for field in form.fields.all():
                if field.field_type == 'hidden' and field.default_value:
                    # Если поле уже заполнено в form_data, не перезаписываем
                    if field.name not in form_data:
                        default = field.default_value
                        # Заменяем плейсхолдеры
                        if service:
                            default = default.replace('{service_title}', service.title)
                        if source_page:
                            default = default.replace('{source_page}', source_page)
                        form_data[field.name] = default
            
            # Проверяем правила формы
            quiz_submission = None
            for rule in form.rules.filter(is_active=True).order_by('order'):
                field_value = form_data.get(rule.field.name, '')
                if str(field_value) == str(rule.field_value) and rule.quiz:
                    # Правило сработало - открываем анкету
                    # Анкета будет обработана на фронтенде
                    pass
            
            # Создаем отправку формы
            try:
                submission = BookingSubmission.objects.create(
                    form=form,
                    service=service,
                    source_page=source_page,
                    data=form_data
                )
                logger.info(f'BookingSubmission создана успешно: id={submission.id}')
            except Exception as e:
                logger.error(f'Ошибка при создании BookingSubmission: {e}', exc_info=True)
                return Response({'error': f'Ошибка при создании заявки: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Запускаем асинхронную обработку интеграций (MoyKlass, Telegram)
            # Не ждем завершения - сразу возвращаем ответ пользователю
            try:
                thread = threading.Thread(
                    target=process_booking_submission_async,
                    args=(submission.id,),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                logger.error(f'Ошибка при запуске асинхронной обработки: {e}', exc_info=True)
                # Не прерываем выполнение, так как заявка уже создана
            
            serializer = self.get_serializer(submission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'Неожиданная ошибка в BookingSubmission.create: {e}', exc_info=True)
            return Response({'error': f'Ошибка при обработке заявки: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def submit_with_quiz(self, request):
        """Отправка формы с результатами анкеты"""
        form_id = request.data.get('form_id')
        service_id = request.data.get('service_id')
        source_page = request.data.get('source_page', '')
        form_data = request.data.get('data', {})
        quiz_submission_id = request.data.get('quiz_submission_id')
        
        try:
            form = BookingForm.objects.get(id=form_id, is_active=True)
        except BookingForm.DoesNotExist:
            return Response({'error': 'Форма не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        service = None
        if service_id:
            try:
                service = Service.objects.get(id=service_id, is_active=True)
            except Service.DoesNotExist:
                pass
        
        # Подставляем значения в скрытые поля
        for field in form.fields.all():
            if field.field_type == 'hidden' and field.default_value:
                # Если поле уже заполнено в form_data, не перезаписываем
                if field.name not in form_data:
                    default = field.default_value
                    # Заменяем плейсхолдеры
                    if service:
                        default = default.replace('{service_title}', service.title)
                    if source_page:
                        default = default.replace('{source_page}', source_page)
                    form_data[field.name] = default
        
        quiz_submission = None
        if quiz_submission_id:
            try:
                quiz_submission = QuizSubmission.objects.get(id=quiz_submission_id)
            except QuizSubmission.DoesNotExist:
                pass
        
        submission = BookingSubmission.objects.create(
            form=form,
            service=service,
            source_page=source_page,
            data=form_data,
            quiz_submission=quiz_submission
        )
        
        # Запускаем асинхронную обработку интеграций (MoyKlass, Telegram)
        # Не ждем завершения - сразу возвращаем ответ пользователю
        thread = threading.Thread(
            target=process_booking_submission_async,
            args=(submission.id,),
            daemon=True
        )
        thread.start()
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

