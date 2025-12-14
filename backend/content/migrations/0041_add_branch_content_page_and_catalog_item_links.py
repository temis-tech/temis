# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0040_add_service_branch_and_price_history'),
    ]

    operations = [
        # Добавляем связь Branch с ContentPage
        migrations.AddField(
            model_name='branch',
            name='content_page',
            field=models.ForeignKey(blank=True, help_text='Страница контента для отображения информации о филиале через конструктор', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='branches', to='content.contentpage', verbose_name='Страница филиала'),
        ),
        # Добавляем связи Service и Branch в CatalogItem
        migrations.AddField(
            model_name='catalogitem',
            name='service',
            field=models.ForeignKey(blank=True, help_text='Если выбрана услуга, элемент каталога будет использовать данные услуги (название, описание, изображение, цены)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='catalog_items', to='content.service', verbose_name='Услуга'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='branch',
            field=models.ForeignKey(blank=True, help_text='Если выбран филиал, элемент каталога будет использовать данные филиала (название, адрес, изображение)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='catalog_items', to='content.branch', verbose_name='Филиал'),
        ),
        # Делаем поле title опциональным (blank=True), так как оно может быть заполнено автоматически из услуги или филиала
        migrations.AlterField(
            model_name='catalogitem',
            name='title',
            field=models.CharField(blank=True, help_text='Автоматически заполняется из услуги или филиала, если они выбраны. Можно переопределить вручную.', max_length=200, verbose_name='Название'),
        ),
    ]
