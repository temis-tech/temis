# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moyklass', '0003_moyklassintegration_moyklassfieldmapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='moyklasssettings',
            name='website_tag_name',
            field=models.CharField(
                default='Пришел с сайта',
                help_text='Тег, который будет автоматически присваиваться лидам, созданным с сайта. Можно выбрать из списка тегов MoyKlass или ввести свой.',
                max_length=200,
                verbose_name='Название тега для лидов с сайта'
            ),
        ),
        migrations.AddField(
            model_name='moyklasssettings',
            name='website_tag_id',
            field=models.IntegerField(
                blank=True,
                help_text='ID тега в MoyKlass (заполняется автоматически при выборе тега)',
                null=True,
                verbose_name='ID тега для лидов с сайта'
            ),
        ),
    ]

