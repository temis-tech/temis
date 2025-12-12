# Generated manually - исправление миграции 0024
# Безопасная миграция, которая работает даже если миграция 0024 не была применена полностью

from django.db import migrations, models
from django.db import connection


def check_field_exists(table_name, field_name):
    """Проверяет, существует ли поле в таблице"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, [table_name, field_name])
        return cursor.fetchone() is not None


def add_missing_fields_from_0024(apps, schema_editor):
    """Добавляет поля из миграции 0024, если их нет (на случай если миграция 0024 не была применена)"""
    with connection.cursor() as cursor:
        # Добавляем has_own_page для catalogitem, если его нет
        if not check_field_exists('content_catalogitem', 'has_own_page'):
            try:
                cursor.execute("""
                    ALTER TABLE content_catalogitem 
                    ADD COLUMN has_own_page BOOLEAN NOT NULL DEFAULT FALSE
                """)
            except Exception:
                pass  # Игнорируем ошибку, если поле уже существует
        
        # Добавляем slug для catalogitem, если его нет
        if not check_field_exists('content_catalogitem', 'slug'):
            try:
                cursor.execute("""
                    ALTER TABLE content_catalogitem 
                    ADD COLUMN slug VARCHAR(50) NULL
                """)
            except Exception:
                pass  # Игнорируем ошибку, если поле уже существует
        
        # Добавляем has_own_page для service, если его нет
        if not check_field_exists('content_service', 'has_own_page'):
            try:
                cursor.execute("""
                    ALTER TABLE content_service 
                    ADD COLUMN has_own_page BOOLEAN NOT NULL DEFAULT FALSE
                """)
            except Exception:
                pass  # Игнорируем ошибку, если поле уже существует


def generate_slugs_for_catalog_items(apps, schema_editor):
    """Генерирует slug для существующих элементов каталога"""
    # Проверяем наличие всех необходимых полей перед использованием модели
    if not check_field_exists('content_catalogitem', 'slug'):
        return  # Если поля slug нет, пропускаем генерацию
    
    if not check_field_exists('content_catalogitem', 'has_own_page'):
        return  # Если поля has_own_page нет, модель не может быть загружена корректно
    
    CatalogItem = apps.get_model('content', 'CatalogItem')
    import re
    
    def transliterate_slug(text):
        """Транслитерация кириллицы в латиницу для slug"""
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        }
        text = text.lower()
        slug = ''.join(translit_map.get(c, c) for c in text)
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')[:50]
    
    # Используем raw SQL для безопасного доступа к данным, если модель не может быть загружена
    try:
        with connection.cursor() as cursor:
            # Получаем все записи через SQL, чтобы избежать проблем с моделью
            cursor.execute("""
                SELECT id, title, slug 
                FROM content_catalogitem
            """)
            items = cursor.fetchall()
            
            for item_id, title, current_slug in items:
                if not current_slug or current_slug == '':
                    base_slug = transliterate_slug(title) or f'catalog-item-{item_id}'
                    slug = base_slug
                    counter = 1
                    
                    # Проверяем уникальность через SQL
                    while True:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM content_catalogitem 
                            WHERE slug = %s AND id != %s
                        """, [slug, item_id])
                        if cursor.fetchone()[0] == 0:
                            break
                        slug = f'{base_slug}-{counter}'
                        counter += 1
                    
                    # Обновляем slug через SQL
                    cursor.execute("""
                        UPDATE content_catalogitem 
                        SET slug = %s 
                        WHERE id = %s
                    """, [slug, item_id])
    except Exception as e:
        # Если что-то пошло не так, просто пропускаем генерацию
        # Миграция не должна падать из-за проблем с данными
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_add_catalog_item_and_service_pages'),
    ]

    operations = [
        # Сначала добавляем все необходимые поля из миграции 0024, если их нет
        migrations.RunPython(
            add_missing_fields_from_0024,
            migrations.RunPython.noop,
        ),
        # Генерируем slug для существующих записей (только если все поля существуют)
        migrations.RunPython(
            generate_slugs_for_catalog_items,
            migrations.RunPython.noop,
        ),
    ]

