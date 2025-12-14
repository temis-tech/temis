# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0042_add_display_branches_to_content_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='selected_catalog_page',
            field=models.ForeignKey(blank=True, help_text='Выберите страницу с типом "Каталог", которая будет отображаться на этой странице (только для типа "Описание")', limit_choices_to={'is_active': True, 'page_type': 'catalog'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='used_as_catalog_in', to='content.contentpage', verbose_name='Каталог для отображения'),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='selected_gallery_page',
            field=models.ForeignKey(blank=True, help_text='Выберите страницу с типом "Галерея", которая будет отображаться на этой странице (только для типа "Описание")', limit_choices_to={'is_active': True, 'page_type': 'gallery'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='used_as_gallery_in', to='content.contentpage', verbose_name='Галерея для отображения'),
        ),
    ]
