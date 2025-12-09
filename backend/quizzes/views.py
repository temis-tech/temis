from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Quiz, Question, AnswerOption, ResultRange, QuizSubmission, SubmissionAnswer
from .serializers import (
    QuizSerializer, QuizSubmissionCreateSerializer, QuizSubmissionSerializer
)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.filter(is_active=True).prefetch_related('questions__options', 'result_ranges')
    serializer_class = QuizSerializer
    lookup_field = 'slug'

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        try:
            quiz = self.queryset.get(slug=slug)
            serializer = self.get_serializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({'error': 'Анкета не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, **kwargs):
        try:
            # Из-за lookup_field='slug' DRF передает slug в kwargs, но URL использует ID
            # Получаем значение из kwargs (может быть как slug, так и pk)
            lookup_value = kwargs.get('slug') or kwargs.get('pk')
            
            if not lookup_value:
                return Response({'error': 'Не указан ID или slug анкетаа'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Пытаемся получить по ID (если это число)
            try:
                quiz_id = int(lookup_value)
                quiz = Quiz.objects.get(id=quiz_id, is_active=True)
            except (ValueError, Quiz.DoesNotExist):
                # Если не число или не найден по ID, пробуем по slug
                try:
                    quiz = self.queryset.get(slug=lookup_value)
                except Quiz.DoesNotExist:
                    return Response({'error': 'Анкета не найден'}, status=status.HTTP_404_NOT_FOUND)
            serializer = QuizSubmissionCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            
            with transaction.atomic():
                # Создаем отправку
                submission = QuizSubmission.objects.create(
                    quiz=quiz,
                    user_name=data.get('user_name') or '',
                    user_phone=data.get('user_phone') or '',
                    user_email=data.get('user_email') or '',
                )
                
                total_points = 0
                
                # Обрабатываем ответы
                for answer_data in data['answers']:
                    question_id = answer_data['question_id']
                    try:
                        question = Question.objects.get(id=question_id, quiz=quiz)
                    except Question.DoesNotExist:
                        continue
                    
                    answer_points = 0
                    selected_options = []
                    
                    if question.question_type == 'text':
                        # Текстовый ответ
                        text_answer = answer_data.get('text_answer', '')
                        submission_answer = SubmissionAnswer.objects.create(
                            submission=submission,
                            question=question,
                            text_answer=text_answer,
                            points=0
                        )
                    else:
                        # Выбор вариантов
                        option_ids = answer_data.get('option_ids', [])
                        if option_ids:
                            selected_options = AnswerOption.objects.filter(
                                id__in=option_ids,
                                question=question
                            )
                            answer_points = sum(opt.points for opt in selected_options)
                            
                            submission_answer = SubmissionAnswer.objects.create(
                                submission=submission,
                                question=question,
                                points=answer_points
                            )
                            submission_answer.selected_options.set(selected_options)
                        else:
                            submission_answer = SubmissionAnswer.objects.create(
                                submission=submission,
                                question=question,
                                points=0
                            )
                    
                    total_points += answer_points
                
                # Обновляем общие баллы
                submission.total_points = total_points
                
                # Определяем результат по баллам
                result_ranges = ResultRange.objects.filter(quiz=quiz).order_by('-min_points')
                for result_range in result_ranges:
                    if result_range.matches_points(total_points):
                        submission.result = result_range
                        break
                
                submission.save()
            
            response_serializer = QuizSubmissionSerializer(submission)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer

