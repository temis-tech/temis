from django.contrib import admin
from .models import BookingForm, FormField, FormRule, BookingSubmission


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1
    fields = ['label', 'name', 'field_type', 'is_required', 'order', 'placeholder', 'default_value']


class FormRuleInline(admin.TabularInline):
    model = FormRule
    extra = 1
    fields = ['field', 'field_value', 'quiz', 'is_active', 'order']
    verbose_name = 'Правило'
    verbose_name_plural = 'Правила'
    
    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related('quiz', 'field')


@admin.register(BookingForm)
class BookingFormAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'default_quiz', 'fields_count', 'submissions_count', 'created_at']
    list_editable = ['is_active']
    list_filter = ['is_active', 'created_at', 'default_quiz']
    search_fields = ['title', 'description']
    readonly_fields = ['default_quiz_status']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Настройки формы', {
            'fields': ('submit_button_text', 'success_message')
        }),
        ('Анкета по умолчанию', {
            'fields': ('default_quiz', 'default_quiz_status'),
            'description': 'Если указана анкета по умолчанию, она будет открываться всегда при отправке формы (без проверки условий). Правила формы будут игнорироваться.'
        }),
    )
    inlines = [FormFieldInline, FormRuleInline]
    
    def default_quiz_status(self, obj):
        """Показывает статус анкеты по умолчанию"""
        if not obj.default_quiz:
            return 'Анкета не установлена'
        if not obj.default_quiz.is_active:
            return '⚠️ Анкета неактивна'
        if not obj.default_quiz.slug:
            return '⚠️ У анкеты нет slug'
        return f'✅ Анкета готова: {obj.default_quiz.title}'
    default_quiz_status.short_description = 'Статус анкеты по умолчанию'
    
    def fields_count(self, obj):
        return obj.fields.count()
    fields_count.short_description = 'Поля'
    
    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = 'Отправок'


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'form', 'field_type', 'is_required', 'order']
    list_editable = ['order', 'is_required']
    list_filter = ['field_type', 'is_required', 'form']
    search_fields = ['label', 'name', 'form__title']
    fieldsets = (
        ('Основная информация', {
            'fields': ('form', 'label', 'name', 'field_type', 'is_required', 'order')
        }),
        ('Настройки поля', {
            'fields': ('placeholder', 'help_text', 'default_value', 'options')
        }),
    )


@admin.register(FormRule)
class FormRuleAdmin(admin.ModelAdmin):
    list_display = ['form', 'field', 'field_value', 'quiz', 'quiz_status', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'form', 'quiz']
    search_fields = ['form__title', 'field__label', 'field_value']
    readonly_fields = ['quiz_status']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('form', 'field', 'field_value', 'order', 'is_active')
        }),
        ('Анкета', {
            'fields': ('quiz', 'quiz_status'),
            'description': 'Выберите анкету, которая откроется при срабатывании правила. Анкета должна быть активна и иметь slug.'
        }),
    )
    
    def quiz_status(self, obj):
        """Показывает статус анкеты"""
        if not obj.quiz:
            return '⚠️ Анкета не выбрана'
        if not obj.quiz.is_active:
            return '⚠️ Анкета неактивна'
        if not obj.quiz.slug:
            return '⚠️ У анкеты нет slug'
        return '✅ Анкета готова к использованию'
    quiz_status.short_description = 'Статус анкеты'


@admin.register(BookingSubmission)
class BookingSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form', 'service', 'source_page', 'created_at', 'user_info']
    list_filter = ['form', 'created_at']
    search_fields = ['form__title', 'service__title', 'source_page']
    readonly_fields = ['form', 'service', 'source_page', 'data', 'quiz_submission', 'created_at']
    
    def user_info(self, obj):
        data = obj.data or {}
        name = data.get('name', '') or data.get('user_name', '')
        phone = data.get('phone', '') or data.get('user_phone', '')
        email = data.get('email', '') or data.get('user_email', '')
        parts = [p for p in [name, phone, email] if p]
        return ' | '.join(parts) if parts else 'Нет данных'
    user_info.short_description = 'Контактные данные'
    
    def has_add_permission(self, request):
        return False

