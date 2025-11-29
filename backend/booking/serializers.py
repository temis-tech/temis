from rest_framework import serializers
from .models import BookingForm, FormField, FormRule, BookingSubmission
from content.serializers import ServiceSerializer
from quizzes.serializers import QuizSerializer


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'name', 'field_type', 'placeholder', 'help_text', 
                 'is_required', 'order', 'default_value', 'options']


class FormRuleSerializer(serializers.ModelSerializer):
    quiz_slug = serializers.SerializerMethodField()
    quiz_title = serializers.SerializerMethodField()
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = FormRule
        fields = ['id', 'field', 'field_name', 'field_value', 'quiz', 'quiz_slug', 'quiz_title', 'is_active', 'order']
    
    def get_quiz_slug(self, obj):
        """Возвращает slug квиза только если квиз активен и имеет slug"""
        if obj.quiz and obj.quiz.is_active and obj.quiz.slug:
            return obj.quiz.slug
        return None
    
    def get_quiz_title(self, obj):
        """Возвращает название квиза только если квиз активен"""
        if obj.quiz and obj.quiz.is_active:
            return obj.quiz.title
        return None


class BookingFormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    rules = serializers.SerializerMethodField()
    default_quiz_slug = serializers.SerializerMethodField()
    default_quiz_title = serializers.SerializerMethodField()
    
    class Meta:
        model = BookingForm
        fields = ['id', 'title', 'description', 'submit_button_text', 'success_message', 
                 'is_active', 'fields', 'rules', 'default_quiz', 'default_quiz_slug', 'default_quiz_title']
    
    def get_rules(self, obj):
        """Возвращает только активные правила, отсортированные по order"""
        active_rules = obj.rules.filter(is_active=True).order_by('order')
        return FormRuleSerializer(active_rules, many=True).data
    
    def get_default_quiz_slug(self, obj):
        """Возвращает slug квиза по умолчанию только если квиз активен и имеет slug"""
        if obj.default_quiz and obj.default_quiz.is_active and obj.default_quiz.slug:
            return obj.default_quiz.slug
        return None
    
    def get_default_quiz_title(self, obj):
        """Возвращает название квиза по умолчанию только если квиз активен"""
        if obj.default_quiz and obj.default_quiz.is_active:
            return obj.default_quiz.title
        return None


class BookingSubmissionSerializer(serializers.ModelSerializer):
    form_title = serializers.CharField(source='form.title', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True, allow_null=True)
    
    class Meta:
        model = BookingSubmission
        fields = ['id', 'form', 'form_title', 'service', 'service_title', 'data', 
                 'quiz_submission', 'created_at']
        read_only_fields = ['created_at']

