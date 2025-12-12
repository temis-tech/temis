# Generated manually - исправление миграции 0024
# Безопасная миграция, которая работает даже если поле slug еще не создано

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


def add_slug_field_if_missing(apps, schema_editor):
    """Добавляет поле slug, если его нет (на случай если миграция 0024 не была применена)"""
    if not check_field_exists('content_catalogitem', 'slug'):
        # Добавляем поле slug через SQL
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    ALTER TABLE content_catalogitem 
                    ADD COLUMN slug VARCHAR(50) NULL
                """)
            except Exception as e:
                # Игнорируем ошибку, если поле уже существует
                pass


def generate_slugs_for_catalog_items(apps, schema_editor):
    """Генерирует slug для существующих элементов каталога"""
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
    
    # Проверяем, существует ли поле slug
    if not check_field_exists('content_catalogitem', 'slug'):
        # Если поля нет, пропускаем генерацию slug
        return
    
    for item in CatalogItem.objects.all():
        if not item.slug or item.slug == '':
            base_slug = transliterate_slug(item.title) or f'catalog-item-{item.id}'
            slug = base_slug
            counter = 1
            # Убеждаемся, что slug уникален
            while CatalogItem.objects.filter(slug=slug).exclude(id=item.id).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            item.slug = slug
            item.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_add_catalog_item_and_service_pages'),
    ]

    operations = [
        # Сначала добавляем поле slug, если его нет
        migrations.RunPython(
            add_slug_field_if_missing,
            migrations.RunPython.noop,
        ),
        # Генерируем slug для существующих записей (только если поле существует)
        migrations.RunPython(
            generate_slugs_for_catalog_items,
            migrations.RunPython.noop,
        ),
    ]

