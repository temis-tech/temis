# Generated manually

import django.db.models.deletion
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
        if not item.slug:
            base_slug = transliterate_slug(item.title) or f'catalog-item-{item.id}'
            slug = base_slug
            counter = 1
            # Убеждаемся, что slug уникален
            while CatalogItem.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            item.slug = slug
            item.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0023_add_banner_display_type_and_blur'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='has_own_page',
            field=models.BooleanField(default=False, help_text='Если включено, карточка будет иметь свой URL и может быть открыта как отдельная страница', verbose_name='Может быть открыт как страница'),
        ),
        # Сначала добавляем slug как nullable, чтобы избежать конфликтов
        migrations.AddField(
            model_name='catalogitem',
            name='slug',
            field=models.SlugField(blank=True, help_text='Автоматически генерируется из названия, если не указан. Используется для создания страницы элемента.', null=True, verbose_name='URL'),
        ),
        # Генерируем slug для существующих записей
        migrations.RunPython(generate_slugs_for_catalog_items, migrations.RunPython.noop),
        # Теперь делаем поле unique и убираем null
        migrations.AlterField(
            model_name='catalogitem',
            name='slug',
            field=models.SlugField(blank=True, help_text='Автоматически генерируется из названия, если не указан. Используется для создания страницы элемента.', unique=True, verbose_name='URL'),
        ),
        migrations.AddField(
            model_name='service',
            name='has_own_page',
            field=models.BooleanField(default=False, help_text='Если включено, услуга будет иметь свой URL и может быть открыта как отдельная страница', verbose_name='Может быть открыта как страница'),
        ),
    ]

