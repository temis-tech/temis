from django.core.management.base import BaseCommand
from content.models import ContentPage, HomePageBlock


class Command(BaseCommand):
    help = 'Проверяет данные главной страницы и её блоков'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Проверка главной страницы ===\n'))
        
        # Ищем главную страницу
        try:
            home_page = ContentPage.objects.get(slug='home', page_type='home')
            self.stdout.write(self.style.SUCCESS(f'✓ Главная страница найдена: "{home_page.title}"'))
            self.stdout.write(f'  - ID: {home_page.id}')
            self.stdout.write(f'  - Slug: {home_page.slug}')
            self.stdout.write(f'  - Тип: {home_page.page_type}')
            self.stdout.write(f'  - Активна: {"Да" if home_page.is_active else "НЕТ!"}')
            self.stdout.write(f'  - Описание: {"Есть" if home_page.description else "Нет"}')
        except ContentPage.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Главная страница НЕ найдена!'))
            self.stdout.write('  Проверьте, что существует страница с slug="home" и page_type="home"')
            return
        except ContentPage.MultipleObjectsReturned:
            self.stdout.write(self.style.ERROR('✗ Найдено несколько главных страниц!'))
            pages = ContentPage.objects.filter(slug='home', page_type='home')
            for page in pages:
                self.stdout.write(f'  - ID: {page.id}, "{page.title}", активна: {page.is_active}')
            return
        
        if not home_page.is_active:
            self.stdout.write(self.style.ERROR('\n✗ Главная страница НЕ активна!'))
            self.stdout.write('  Включите страницу в админке (is_active=True)')
            return
        
        # Проверяем блоки
        self.stdout.write(self.style.SUCCESS('\n=== Проверка блоков главной страницы ===\n'))
        
        all_blocks = HomePageBlock.objects.filter(page=home_page)
        active_blocks = all_blocks.filter(is_active=True)
        
        self.stdout.write(f'Всего блоков: {all_blocks.count()}')
        self.stdout.write(f'Активных блоков: {active_blocks.count()}\n')
        
        if active_blocks.count() == 0:
            self.stdout.write(self.style.WARNING('⚠ Нет активных блоков!'))
            self.stdout.write('  Добавьте блоки в админке и убедитесь, что они активны')
        else:
            self.stdout.write(self.style.SUCCESS('Активные блоки:'))
            for i, block in enumerate(active_blocks.order_by('order'), 1):
                self.stdout.write(f'\n  Блок #{i} (ID: {block.id}):')
                self.stdout.write(f'    - Заголовок: {block.title or "(используется заголовок страницы)"}')
                self.stdout.write(f'    - Показывать заголовок: {"Да" if block.show_title else "Нет"}')
                self.stdout.write(f'    - Порядок: {block.order}')
                self.stdout.write(f'    - Активен: {"Да" if block.is_active else "НЕТ!"}')
                
                if block.content_page:
                    content_page = block.content_page
                    self.stdout.write(f'    - Страница контента: "{content_page.title}" (ID: {content_page.id})')
                    self.stdout.write(f'      • Slug: {content_page.slug}')
                    self.stdout.write(f'      • Тип: {content_page.page_type}')
                    self.stdout.write(f'      • Активна: {"Да" if content_page.is_active else "НЕТ!"}')
                    
                    if content_page.page_type == 'home':
                        self.stdout.write(self.style.WARNING('      ⚠ ВНИМАНИЕ: Страница типа "home" не должна быть в блоках!'))
                    
                    # Проверяем данные в зависимости от типа страницы
                    if content_page.page_type == 'text':
                        self.stdout.write(f'      • Описание: {"Есть" if content_page.description else "Нет"}')
                        self.stdout.write(f'      • Изображение: {"Есть" if content_page.image else "Нет"}')
                        if content_page.selected_catalog_page:
                            self.stdout.write(f'      • Выбранный каталог: "{content_page.selected_catalog_page.title}"')
                        if content_page.selected_gallery_page:
                            self.stdout.write(f'      • Выбранная галерея: "{content_page.selected_gallery_page.title}"')
                    
                    elif content_page.page_type == 'faq':
                        faq_items = content_page.faq_items.filter(is_active=True)
                        self.stdout.write(f'      • Элементы FAQ: {faq_items.count()} активных')
                        if faq_items.count() == 0:
                            self.stdout.write(self.style.WARNING('      ⚠ Нет активных элементов FAQ!'))
                        else:
                            self.stdout.write('      • FAQ элементы:')
                            for item in faq_items.order_by('order')[:3]:
                                self.stdout.write(f'        - "{item.question[:50]}..."')
                            if faq_items.count() > 3:
                                self.stdout.write(f'        ... и еще {faq_items.count() - 3}')
                    
                    elif content_page.page_type == 'catalog':
                        catalog_items = content_page.catalog_items.filter(is_active=True)
                        self.stdout.write(f'      • Элементы каталога: {catalog_items.count()} активных')
                    
                    elif content_page.page_type == 'gallery':
                        gallery_images = content_page.gallery_images.filter(is_active=True)
                        self.stdout.write(f'      • Изображения галереи: {gallery_images.count()} активных')
                else:
                    self.stdout.write(self.style.ERROR('    ✗ Страница контента не выбрана!'))
        
        # Проверяем неактивные блоки
        inactive_blocks = all_blocks.filter(is_active=False)
        if inactive_blocks.count() > 0:
            self.stdout.write(self.style.WARNING(f'\n⚠ Неактивных блоков: {inactive_blocks.count()}'))
            self.stdout.write('  (Эти блоки не будут отображаться на сайте)')
        
        self.stdout.write(self.style.SUCCESS('\n=== Проверка завершена ==='))
