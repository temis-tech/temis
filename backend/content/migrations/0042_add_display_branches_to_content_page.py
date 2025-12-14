# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0041_add_branch_content_page_and_catalog_item_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='display_branches',
            field=models.ManyToManyField(blank=True, help_text='Выберите филиалы, которые будут отображаться на этой странице. Можно использовать для создания страницы контактов или страницы с информацией о филиалах.', related_name='displayed_on_pages', to='content.branch', verbose_name='Филиалы для отображения'),
        ),
    ]
