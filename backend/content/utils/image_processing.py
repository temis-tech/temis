"""
Утилиты для обработки и оптимизации изображений
"""
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def optimize_image(image_field, max_width=1920, max_height=1920, quality=85, format='JPEG'):
    """
    Оптимизирует изображение для веб:
    - Изменяет размер если нужно
    - Сжимает с заданным качеством
    - Конвертирует в нужный формат
    
    Args:
        image_field: Django ImageField
        max_width: максимальная ширина (по умолчанию 1920px)
        max_height: максимальная высота (по умолчанию 1920px)
        quality: качество JPEG (1-100, по умолчанию 85)
        format: формат выходного файла ('JPEG', 'PNG', 'WEBP')
    
    Returns:
        True если обработка прошла успешно, False в противном случае
    """
    if not image_field or not hasattr(image_field, 'file') or not image_field.file:
        return False
    
    try:
        # Сохраняем текущую позицию файла
        image_field.file.seek(0)
        
        # Открываем изображение
        img = Image.open(image_field.file)
        
        # Конвертируем RGBA в RGB для JPEG
        if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            # Создаем белый фон для прозрачных изображений
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB' and format == 'JPEG':
            img = img.convert('RGB')
        
        # Получаем текущие размеры
        width, height = img.size
        
        # Изменяем размер если изображение слишком большое
        if width > max_width or height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Сохраняем в буфер
        output = BytesIO()
        
        # Выбираем формат сохранения
        if format == 'JPEG':
            img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
            ext = 'jpg'
        elif format == 'WEBP':
            img.save(output, format='WEBP', quality=quality, method=6)
            ext = 'webp'
        elif format == 'PNG':
            # Для PNG используем оптимизацию
            img.save(output, format='PNG', optimize=True)
            ext = 'png'
        else:
            img.save(output, format=format, quality=quality)
            ext = format.lower()
        
        # Получаем только имя файла без пути (чтобы избежать дублирования путей)
        # image_field.name может содержать полный путь типа "logo/logo/logo/file.jpg"
        # Нужно взять только имя файла, чтобы Django правильно применил upload_to
        original_name = os.path.basename(image_field.name)  # Получаем только имя файла
        file_name_without_ext = os.path.splitext(original_name)[0]  # Убираем расширение
        new_file_name = f"{file_name_without_ext}.{ext}"  # Новое имя с правильным расширением
        
        # Сохраняем оптимизированное изображение
        # Django автоматически добавит upload_to путь из модели
        image_field.save(
            new_file_name,
            ContentFile(output.getvalue()),
            save=False
        )
        
        return True
        
    except Exception as e:
        # В случае ошибки логируем и возвращаем False
        import traceback
        print(f"Ошибка при обработке изображения: {e}")
        print(traceback.format_exc())
        return False


def process_uploaded_image(image_field, image_type='general'):
    """
    Обрабатывает загруженное изображение в зависимости от типа
    
    Args:
        image_field: Django ImageField
        image_type: тип изображения ('general', 'thumbnail', 'hero', 'avatar')
    
    Returns:
        Обработанное изображение
    """
    # Настройки для разных типов изображений
    settings = {
        'general': {
            'max_width': 1920,
            'max_height': 1920,
            'quality': 85,
            'format': 'JPEG'
        },
        'thumbnail': {
            'max_width': 400,
            'max_height': 400,
            'quality': 80,
            'format': 'JPEG'
        },
        'hero': {
            'max_width': 2560,
            'max_height': 1440,
            'quality': 90,
            'format': 'JPEG'
        },
        'avatar': {
            'max_width': 400,
            'max_height': 400,
            'quality': 85,
            'format': 'JPEG'
        }
    }
    
    config = settings.get(image_type, settings['general'])
    return optimize_image(
        image_field,
        max_width=config['max_width'],
        max_height=config['max_height'],
        quality=config['quality'],
        format=config['format']
    )

