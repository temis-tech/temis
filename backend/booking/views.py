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
        form_id = request.data.get('form_id')
        service_id = request.data.get('service_id')
        source_page = request.data.get('source_page', '')
        form_data = request.data.get('data', {})
        
        # Логируем входящие данные для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'BookingSubmission create: form_id={form_id}, service_id={service_id}, source_page={source_page}, data={form_data}')
        
        try:
            form = BookingForm.objects.get(id=form_id, is_active=True)
        except BookingForm.DoesNotExist:
            return Response({'error': 'Форма не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        service = None
        if service_id:
            try:
                service = Service.objects.get(id=service_id, is_active=True)
                # Подставляем название услуги в скрытые поля
                for field in form.fields.all():
                    if field.field_type == 'hidden' and field.default_value:
                        default = field.default_value.replace('{service_title}', service.title)
                        if field.name not in form_data:
                            form_data[field.name] = default
            except Service.DoesNotExist:
                pass
        
        # Проверяем правила формы
        quiz_submission = None
        for rule in form.rules.filter(is_active=True).order_by('order'):
            field_value = form_data.get(rule.field.name, '')
            if str(field_value) == str(rule.field_value) and rule.quiz:
                # Правило сработало - открываем анкету
                # Анкета будет обработана на фронтенде
                pass
        
        # Создаем отправку формы
        submission = BookingSubmission.objects.create(
            form=form,
            service=service,
            source_page=source_page,
            data=form_data
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
    
    @action(detail=False, methods=['post'])
    def submit_with_quiz(self, request):
        """Отправка формы с результатами анкеты"""
        form_id = request.data.get('form_id')
        service_id = request.data.get('service_id')
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
        
        quiz_submission = None
        if quiz_submission_id:
            try:
                quiz_submission = QuizSubmission.objects.get(id=quiz_submission_id)
            except QuizSubmission.DoesNotExist:
                pass
        
        submission = BookingSubmission.objects.create(
            form=form,
            service=service,
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

