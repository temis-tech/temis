from django.core.management.base import BaseCommand
from content.models import ContentPage
from content.serializers import ContentPageSerializer
from django.test import RequestFactory
import json


class Command(BaseCommand):
    help = 'Проверяет значение show_title для всех страниц или конкретной страницы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Slug страницы для проверки (если не указан, проверяются все страницы)',
        )

    def handle(self, *args, **options):
        slug = options.get('slug')
        
        # Создаем фейковый request для сериализатора
        factory = RequestFactory()
        request = factory.get('/api/content/pages/')
        
        if slug:
            # Проверяем конкретную страницу
            try:
                page = ContentPage.objects.get(slug=slug)
                self.check_page(page, request)
            except ContentPage.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Страница со slug "{slug}" не найдена'))
        else:
            # Проверяем все страницы
            pages = ContentPage.objects.all().order_by('page_type', 'title')
            self.stdout.write(self.style.SUCCESS(f'\nНайдено страниц: {pages.count()}\n'))
            self.stdout.write('=' * 80)
            
            for page in pages:
                self.check_page(page, request)
                self.stdout.write('-' * 80)

    def check_page(self, page, request):
        """Проверяет одну страницу"""
        self.stdout.write(f'\n📄 Страница: {page.title}')
        self.stdout.write(f'   ID: {page.id}')
        self.stdout.write(f'   Slug: {page.slug}')
        self.stdout.write(f'   Тип: {page.page_type}')
        
        # Значение в БД
        db_value = page.show_title
        self.stdout.write(f'\n   🔍 В базе данных:')
        self.stdout.write(f'      show_title = {db_value} (тип: {type(db_value).__name__})')
        self.stdout.write(f'      show_title == True: {db_value == True}')
        self.stdout.write(f'      show_title == False: {db_value == False}')
        self.stdout.write(f'      bool(show_title): {bool(db_value)}')
        
        # Значение в сериализаторе
        serializer = ContentPageSerializer(page, context={'request': request})
        data = serializer.data
        serialized_value = data.get('show_title')
        
        self.stdout.write(f'\n   📤 В сериализованных данных (API):')
        self.stdout.write(f'      show_title = {serialized_value} (тип: {type(serialized_value).__name__})')
        self.stdout.write(f'      show_title == True: {serialized_value == True}')
        self.stdout.write(f'      show_title == False: {serialized_value == False}')
        self.stdout.write(f'      bool(show_title): {bool(serialized_value)}')
        
        # Проверка соответствия
        if db_value != serialized_value:
            self.stdout.write(self.style.WARNING(
                f'\n   ⚠️  ВНИМАНИЕ: Значение в БД ({db_value}) не совпадает со значением в API ({serialized_value})!'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n   ✅ Значения совпадают'
            ))

