# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0062_add_card_short_description_and_remove_duration'),
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='booking_button_text',
            field=models.CharField(blank=True, default='Записаться', help_text='Текст кнопки записи, которая отображается на странице услуги', max_length=100, verbose_name='Текст кнопки записи на странице'),
        ),
        migrations.AddField(
            model_name='service',
            name='booking_form_on_page',
            field=models.ForeignKey(blank=True, help_text='Форма записи, которая откроется при нажатии на кнопку на странице услуги. Если не указана, используется основная форма записи.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services_page', to='booking.bookingform', verbose_name='Форма записи на странице'),
        ),
        migrations.AddField(
            model_name='service',
            name='show_booking_button_on_page',
            field=models.BooleanField(default=False, help_text='Отображать кнопку записи на странице детального просмотра услуги', verbose_name='Показывать кнопку записи на странице услуги'),
        ),
    ]

