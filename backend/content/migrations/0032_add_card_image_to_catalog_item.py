# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0030_update_privacy_policy_to_policies'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='card_image',
            field=models.ImageField(blank=True, null=True, upload_to='catalog/cards/', verbose_name='Изображение для карточки', help_text='Изображение, которое будет отображаться в карточке элемента в списке каталога'),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='catalog/', verbose_name='Изображение для страницы', help_text='Изображение, которое будет отображаться на странице элемента (если включен режим "Может быть открыт как страница")'),
        ),
    ]
