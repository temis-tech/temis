from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, AnswerOption, ResultRange, QuizSubmission, SubmissionAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 2
    fields = ['text', 'points', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'question_type', 'order', 'is_required']
    list_filter = ['quiz', 'question_type', 'is_required']
    list_editable = ['order', 'is_required']
    search_fields = ['text']
    inlines = [AnswerOptionInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'order', 'is_required']
    show_change_link = True


class ResultRangeInline(admin.TabularInline):
    model = ResultRange
    extra = 1
    fields = ['min_points', 'max_points', 'title', 'order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'questions_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline, ResultRangeInline]

    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Вопросов'


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'points', 'order']
    list_filter = ['question__quiz']
    list_editable = ['points', 'order']
    search_fields = ['text']


@admin.register(ResultRange)
class ResultRangeAdmin(admin.ModelAdmin):
    list_display = ['title', 'quiz', 'points_range', 'order']
    list_filter = ['quiz']
    list_editable = ['order']
    search_fields = ['title', 'description']

    def points_range(self, obj):
        if obj.max_points:
            return f'{obj.min_points}-{obj.max_points}'
        return f'от {obj.min_points}'
    points_range.short_description = 'Диапазон баллов'


class SubmissionAnswerInline(admin.TabularInline):
    model = SubmissionAnswer
    extra = 0
    readonly_fields = ['question', 'selected_options', 'text_answer', 'points']
    can_delete = False


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'user_name', 'user_phone', 'total_points', 'result', 'created_at']
    list_filter = ['quiz', 'result', 'created_at']
    search_fields = ['user_name', 'user_phone', 'user_email']
    readonly_fields = ['quiz', 'total_points', 'result', 'created_at']
    inlines = [SubmissionAnswerInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'points', 'created_at']
    list_filter = ['submission__quiz', 'created_at']
    readonly_fields = ['submission', 'question', 'selected_options', 'text_answer', 'points', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

