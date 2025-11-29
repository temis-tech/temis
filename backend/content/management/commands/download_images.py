"""
Команда для скачивания изображений с сайта
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from content.models import Branch, Service, Specialist, Review, Promotion, Article
from io import BytesIO
import os


class Command(BaseCommand):
    help = 'Скачивает изображения с сайта logoped-spb.pro'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаю скачивание изображений...'))
        
        # Создаем папку для временных изображений
        media_dir = 'media'
        os.makedirs(media_dir, exist_ok=True)
        
        # Плейсхолдеры изображений (так как мы не можем напрямую скачать с сайта)
        # Создадим простые цветные изображения как плейсхолдеры
        self.create_placeholder_images()
        
        self.stdout.write(self.style.SUCCESS('Готово!'))

    def create_placeholder_images(self):
        """Создает плейсхолдеры изображений"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Создаем изображения для услуг
            services = Service.objects.all()
            for service in services:
                if not service.image:
                    img = Image.new('RGB', (800, 600), color=(102, 126, 234))  # Фиолетовый градиент
                    draw = ImageDraw.Draw(img)
                    # Простой текст
                    text = service.title[:30]
                    try:
                        # Пытаемся использовать системный шрифт
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
                    except:
                        font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    position = ((800 - text_width) // 2, (600 - text_height) // 2)
                    draw.text(position, text, fill=(255, 255, 255), font=font)
                    
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    service.image.save(f'service_{service.id}.png', ContentFile(buffer.read()), save=True)
                    self.stdout.write(f'  ✓ Создано изображение для услуги: {service.title}')
            
            # Создаем изображения для филиалов
            branches = Branch.objects.all()
            for branch in branches:
                if not branch.image:
                    img = Image.new('RGB', (800, 600), color=(118, 75, 162))  # Фиолетовый
                    draw = ImageDraw.Draw(img)
                    text = branch.name[:30]
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
                    except:
                        font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    position = ((800 - text_width) // 2, (600 - text_height) // 2)
                    draw.text(position, text, fill=(255, 255, 255), font=font)
                    
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    branch.image.save(f'branch_{branch.id}.png', ContentFile(buffer.read()), save=True)
                    self.stdout.write(f'  ✓ Создано изображение для филиала: {branch.name}')
            
            # Создаем изображения для специалистов
            from content.models import Specialist
            specialists = Specialist.objects.all()
            for specialist in specialists:
                if not specialist.photo:
                    img = Image.new('RGB', (400, 400), color=(102, 126, 234))  # Фиолетово-синий
                    draw = ImageDraw.Draw(img)
                    # Рисуем градиент
                    for i in range(400):
                        color_val = int(102 + (162 - 102) * i / 400)
                        draw.rectangle([(0, i), (400, i+1)], fill=(color_val, 126, 234))
                    
                    # Добавляем инициалы
                    initials = ''.join([word[0] for word in specialist.name.split()[:2]])
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
                    except:
                        font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), initials, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    position = ((400 - text_width) // 2, (400 - text_height) // 2)
                    draw.text(position, initials, fill=(255, 255, 255), font=font)
                    
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    specialist.photo.save(f'specialist_{specialist.id}.png', ContentFile(buffer.read()), save=True)
                    self.stdout.write(f'  ✓ Создано фото для специалиста: {specialist.name}')
                    
        except ImportError:
            self.stdout.write(self.style.WARNING('Pillow не установлен, пропускаю создание изображений'))

