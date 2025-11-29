from rest_framework import serializers
from django.conf import settings
from .models import Quiz, Question, AnswerOption, ResultRange, QuizSubmission, SubmissionAnswer
from content.serializers import get_image_url


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'points', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'order', 'options']


class ResultRangeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultRange
        fields = ['id', 'min_points', 'max_points', 'title', 'description', 'image', 'order']
    
    def get_image(self, obj):
        return get_image_url(obj.image, self.context.get('request'))


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    result_ranges = ResultRangeSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'slug', 'description', 'questions', 'result_ranges']


class SubmissionAnswerCreateSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    text_answer = serializers.CharField(required=False, allow_blank=True)


class QuizSubmissionCreateSerializer(serializers.Serializer):
    """Сериализатор для создания отправки квиза"""
    answers = SubmissionAnswerCreateSerializer(many=True)
    user_name = serializers.CharField(required=False, allow_blank=True, default='')
    user_phone = serializers.CharField(required=False, allow_blank=True, default='')
    user_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True, default='')
    
    def validate_user_email(self, value):
        """Валидация email - пустая строка преобразуется в None"""
        if value == '':
            return None
        return value


class SubmissionAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_options_text = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionAnswer
        fields = ['id', 'question', 'question_text', 'selected_options', 'selected_options_text', 
                 'text_answer', 'points']

    def get_selected_options_text(self, obj):
        return [opt.text for opt in obj.selected_options.all()]


class QuizSubmissionSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    result_title = serializers.SerializerMethodField()
    answers = SubmissionAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ['id', 'quiz', 'quiz_title', 'total_points', 'result', 'result_title', 
                 'user_name', 'user_phone', 'user_email', 'answers', 'created_at']
    
    def get_result_title(self, obj):
        """Возвращает заголовок результата, если он есть"""
        if obj.result:
            return obj.result.title
        return None

