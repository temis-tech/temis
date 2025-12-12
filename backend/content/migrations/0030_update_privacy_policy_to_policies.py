# Generated manually

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    """Заполняет slug для существующих записей"""
    PrivacyPolicy = apps.get_model('content', 'PrivacyPolicy')
    for policy in PrivacyPolicy.objects.all():
        if not policy.slug:
            base_slug = slugify(policy.title)
            slug = base_slug
            counter = 1
            while PrivacyPolicy.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            policy.slug = slug
            policy.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0029_add_social_network'),
    ]

    operations = [
        # Добавляем новые поля (сначала nullable для существующих записей)
        migrations.AddField(
            model_name='privacypolicy',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, null=True, blank=True, verbose_name='URL-адрес'),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='order',
            field=models.IntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='privacypolicy',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создана'),
        ),
        # Заполняем slug для существующих записей
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        # Обновляем verbose_name
        migrations.AlterModelOptions(
            name='privacypolicy',
            options={'ordering': ['order', 'title'], 'verbose_name': 'Политика', 'verbose_name_plural': 'Политики'},
        ),
        # Делаем slug обязательным после заполнения
        migrations.AlterField(
            model_name='privacypolicy',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, verbose_name='URL-адрес'),
        ),
    ]
