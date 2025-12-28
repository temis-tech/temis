from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Lead, Client, ClientFile, LeadStatus


@admin.register(LeadStatus)
class LeadStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color_display', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'code']
    search_fields = ['name']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Цвет'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_display', 'phone_display', 'email_display', 'status', 'source', 'created_at']
    list_filter = ['status', 'created_at', 'source']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'converted_at', 'booking_submission_link', 'quiz_submission_link']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'phone', 'email', 'status', 'source')
        }),
        ('Связи', {
            'fields': ('booking_submission', 'booking_submission_link', 'quiz_submission', 'quiz_submission_link')
        }),
        ('Дополнительно', {
            'fields': ('additional_data', 'notes', 'created_at', 'updated_at', 'converted_at')
        }),
    )
    
    def name_display(self, obj):
        return obj.get_name() or '-'
    name_display.short_description = 'Имя'
    
    def phone_display(self, obj):
        return obj.get_phone() or '-'
    phone_display.short_description = 'Телефон'
    
    def email_display(self, obj):
        return obj.get_email() or '-'
    email_display.short_description = 'Email'
    
    def booking_submission_link(self, obj):
        if obj.booking_submission:
            url = reverse('admin:booking_bookingsubmission_change', args=[obj.booking_submission.pk])
            return format_html('<a href="{}">Открыть отправку формы</a>', url)
        return '-'
    booking_submission_link.short_description = 'Ссылка на отправку формы'
    
    def quiz_submission_link(self, obj):
        if obj.quiz_submission:
            url = reverse('admin:quizzes_quizsubmission_change', args=[obj.quiz_submission.pk])
            return format_html('<a href="{}">Открыть отправку анкеты</a>', url)
        return '-'
    quiz_submission_link.short_description = 'Ссылка на отправку анкеты'
    
    actions = ['convert_to_client']
    
    def convert_to_client(self, request, queryset):
        """Превратить выбранные лиды в клиентов"""
        count = 0
        for lead in queryset:
            if not lead.status or lead.status.code != 'converted':
                client = lead.convert_to_client()
                if client:
                    count += 1
        self.message_user(request, f'Превращено в клиентов: {count}')
    convert_to_client.short_description = 'Превратить в клиентов'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_display', 'phone_display', 'email_display', 'source_lead_link', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'source_lead_link']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'phone', 'email', 'is_active')
        }),
        ('Связи', {
            'fields': ('source_lead', 'source_lead_link')
        }),
        ('Дополнительно', {
            'fields': ('additional_data_json', 'notes', 'created_at', 'updated_at')
        }),
    )
    
    def name_display(self, obj):
        return obj.get_name() or '-'
    name_display.short_description = 'Имя'
    
    def phone_display(self, obj):
        return obj.get_phone() or '-'
    phone_display.short_description = 'Телефон'
    
    def email_display(self, obj):
        return obj.get_email() or '-'
    email_display.short_description = 'Email'
    
    def source_lead_link(self, obj):
        if obj.source_lead:
            url = reverse('admin:crm_lead_change', args=[obj.source_lead.pk])
            return format_html('<a href="{}">Открыть лид</a>', url)
        return '-'
    source_lead_link.short_description = 'Ссылка на исходный лид'


@admin.register(ClientFile)
class ClientFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'get_display_name', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['client__name', 'name', 'file']
    readonly_fields = ['created_at', 'uploaded_by']
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Название файла'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Только при создании
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
