# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0043_add_selected_catalog_and_gallery_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='item_type',
            field=models.CharField(
                choices=[('link', 'Обычная ссылка'), ('branch_selector', 'Селектор филиала')],
                default='link',
                help_text='Выберите тип пункта меню. "Селектор филиала" отобразит выбор филиала в меню.',
                max_length=20,
                verbose_name='Тип пункта'
            ),
        ),
    ]
