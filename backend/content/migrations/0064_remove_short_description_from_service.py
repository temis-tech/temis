# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0063_add_booking_button_on_page_settings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='short_description',
        ),
    ]

