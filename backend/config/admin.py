from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class CustomAdminSite(admin.AdminSite):
    """Кастомный AdminSite для группировки моделей"""
    
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
                'headersettings',
                'menu',
                'menuitem',
                'contact',
                'footersettings',
                'socialnetwork',
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
