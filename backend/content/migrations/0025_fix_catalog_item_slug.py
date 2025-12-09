# Generated manually - исправление миграции 0024

from django.db import migrations, models


def generate_slugs_for_catalog_items(apps, schema_editor):
    """Генерирует slug для существующих элементов каталога"""
    CatalogItem = apps.get_model('content', 'CatalogItem')
    from django.utils.text import slugify
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
        # Временно убираем unique constraint
        migrations.AlterField(
            model_name='catalogitem',
            name='slug',
            field=models.SlugField(blank=True, help_text='Автоматически генерируется из названия, если не указан. Используется для создания страницы элемента.', null=True, verbose_name='URL'),
        ),
        # Генерируем slug для существующих записей
        migrations.RunPython(generate_slugs_for_catalog_items, migrations.RunPython.noop),
        # Возвращаем unique constraint
        migrations.AlterField(
            model_name='catalogitem',
            name='slug',
            field=models.SlugField(blank=True, help_text='Автоматически генерируется из названия, если не указан. Используется для создания страницы элемента.', unique=True, verbose_name='URL'),
        ),
    ]

