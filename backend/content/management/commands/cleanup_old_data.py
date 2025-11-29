"""
Команда для очистки старых данных из БД
Удаляет Service, Article, Promotion, Specialist, Branch, Review
"""
from django.core.management.base import BaseCommand
from content.models import Service, Article, Promotion, Specialist, Branch, Review


class Command(BaseCommand):
    help = 'Очищает старые данные из БД (Service, Article, Promotion, Specialist, Branch, Review)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтвердить удаление (без этого флага команда только покажет что будет удалено)',
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        
        # Подсчитываем количество записей
        services_count = Service.objects.count()
        articles_count = Article.objects.count()
        promotions_count = Promotion.objects.count()
        specialists_count = Specialist.objects.count()
        branches_count = Branch.objects.count()
        reviews_count = Review.objects.count()
        
        total = services_count + articles_count + promotions_count + specialists_count + branches_count + reviews_count
        
        self.stdout.write(self.style.WARNING(f'\n📊 Статистика данных для удаления:'))
        self.stdout.write(f'  - Services: {services_count}')
        self.stdout.write(f'  - Articles: {articles_count}')
        self.stdout.write(f'  - Promotions: {promotions_count}')
        self.stdout.write(f'  - Specialists: {specialists_count}')
        self.stdout.write(f'  - Branches: {branches_count}')
        self.stdout.write(f'  - Reviews: {reviews_count}')
        self.stdout.write(self.style.WARNING(f'  Всего записей: {total}\n'))
        
        if not confirm:
            self.stdout.write(self.style.ERROR('⚠️  Это только предпросмотр. Для реального удаления используйте --confirm'))
            return
        
        # Удаляем данные
        self.stdout.write(self.style.WARNING('🗑️  Начинаю удаление...'))
        
        deleted_services = Service.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено Services: {deleted_services[0]}'))
        
        deleted_articles = Article.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено Articles: {deleted_articles[0]}'))
        
        deleted_promotions = Promotion.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено Promotions: {deleted_promotions[0]}'))
        
        deleted_specialists = Specialist.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено Specialists: {deleted_specialists[0]}'))
        
        deleted_branches = Branch.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено Branches: {deleted_branches[0]}'))
        
        deleted_reviews = Review.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Удалено Reviews: {deleted_reviews[0]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Очистка завершена! Всего удалено записей: {total}'))

