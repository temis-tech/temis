from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.conf import settings
import os
import re
from pathlib import Path


class CustomAdminSite(admin.AdminSite):
    """Кастомный AdminSite для группировки моделей"""
    site_header = "Администрирование сайта"
    site_title = "Админ-панель TEMIS"
    index_title = "Добро пожаловать в админ-панель"
    
    def get_urls(self):
        """Добавляем кастомные URL для админки"""
        urls = super().get_urls()
        custom_urls = [
            path('instruction/', self.admin_view(self.instruction_view), name='admin_instruction'),
        ]
        return custom_urls + urls
    
    def instruction_view(self, request):
        """Отображение инструкции по управлению сайтом"""
        # Путь к файлу инструкции - на сервере файл находится в /var/www/temis/
        # BASE_DIR указывает на /var/www/temis/backend, поэтому parent будет /var/www/temis
        base_dir = Path(settings.BASE_DIR).parent
        instruction_path = base_dir / 'ИНСТРУКЦИЯ_ПО_УПРАВЛЕНИЮ_САЙТОМ.md'
        
        # Если файл не найден, пробуем альтернативные пути
        if not instruction_path.exists():
            # Пробуем в корне backend (если файл был скопирован туда)
            instruction_path = Path(settings.BASE_DIR) / 'ИНСТРУКЦИЯ_ПО_УПРАВЛЕНИЮ_САЙТОМ.md'
        
        # Если все еще не найден, пробуем абсолютный путь
        if not instruction_path.exists():
            instruction_path = Path('/var/www/temis/ИНСТРУКЦИЯ_ПО_УПРАВЛЕНИЮ_САЙТОМ.md')
        
        # Читаем содержимое инструкции
        content = ""
        if instruction_path.exists():
            try:
                with open(instruction_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"Ошибка при чтении инструкции: {e}"
        else:
            content = f"Файл инструкции не найден. Искали по пути: {instruction_path}"
        
        # Конвертируем Markdown в HTML (простая конвертация)
        html_content = self._markdown_to_html(content)
        
        context = {
            **self.each_context(request),
            'title': 'Инструкция по управлению сайтом',
            'content': html_content,
            'opts': {'app_label': 'admin', 'model_name': 'instruction'},
        }
        return TemplateResponse(request, 'admin/instruction.html', context)
    
    def _markdown_to_html(self, markdown_text):
        """Простая конвертация Markdown в HTML"""
        html = markdown_text
        
        # Заголовки
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Жирный текст
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Курсив
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Ссылки
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Списки
        lines = html.split('\n')
        in_list = False
        result = []
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                if not in_list:
                    result.append('<ol>')
                    in_list = True
                cleaned_line = re.sub(r'^\d+\.\s*', '', line.strip())
                result.append(f'<li>{cleaned_line}</li>')
            else:
                if in_list:
                    result.append('</ul>' if '<ol>' not in '\n'.join(result[-10:]) else '</ol>')
                    in_list = False
                if line.strip():
                    result.append(f'<p>{line}</p>')
                else:
                    result.append('<br>')
        if in_list:
            result.append('</ul>')
        html = '\n'.join(result)
        
        # Код
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        return html
    
    def index(self, request, extra_context=None):
        """Переопределяем главную страницу админки для добавления ссылки на инструкцию"""
        extra_context = extra_context or {}
        extra_context['show_instruction_link'] = True
        return super().index(request, extra_context)
    
    def get_app_list(self, request, app_label=None):
        """
        Переопределяем порядок и группировку приложений в админке
        
        Args:
            request: HTTP request
            app_label: Optional app label when viewing a specific app
        """
        app_list = super().get_app_list(request, app_label)
        
        # Находим приложение content
        content_app = None
        for app in app_list:
            if app['app_label'] == 'content':
                content_app = app
                break
        
        if content_app:
            # Разделяем модели на группы
            header_footer_models = []
            other_models = []
            
            header_footer_model_names = [
                'menu',
                'menuitem',
                'headersettings',
                'footersettings',
                'socialnetwork',
                'contact',
                'privacypolicy'
            ]
            
            # Разделяем модели на группы
            for model in content_app['models']:
                if model['object_name'].lower() in header_footer_model_names:
                    header_footer_models.append(model)
                else:
                    other_models.append(model)
            
            # Сортируем модели шапки и подвала в нужном порядке
            header_footer_models_sorted = []
            for model_name in header_footer_model_names:
                for model in header_footer_models:
                    if model['object_name'].lower() == model_name:
                        header_footer_models_sorted.append(model)
                        break
            
            # Создаем виртуальное приложение для "Шапка и Подвал"
            if header_footer_models_sorted:
                header_footer_app = {
                    'name': 'Шапка и Подвал',
                    'app_label': 'header_footer',
                    'app_url': '/admin/content/',
                    'has_module_perms': True,
                    'models': header_footer_models_sorted
                }
                
                # Вставляем "Шапка и Подвал" перед "Контент"
                content_index = app_list.index(content_app)
                app_list.insert(content_index, header_footer_app)
                
                # Обновляем список моделей в content (убираем модели шапки и подвала)
                content_app['models'] = other_models
        
        return app_list


class CustomAdminConfig(AdminConfig):
    default_site = 'config.admin.CustomAdminSite'

