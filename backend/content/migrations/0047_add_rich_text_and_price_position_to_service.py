# Generated manually
from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0046_add_display_services_to_content_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='description',
            field=ckeditor.fields.RichTextField(
                blank=True,
                help_text='Описание услуги с поддержкой форматирования текста',
                verbose_name='Описание'
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='price_duration_position',
            field=models.CharField(
                choices=[('top', 'Сверху текста'), ('bottom', 'Снизу текста'), ('hidden', 'Не отображать')],
                default='top',
                help_text='Где отображать блоки с ценой и длительностью относительно описания',
                max_length=10,
                verbose_name='Расположение блоков цены и длительности'
            ),
        ),
    ]
