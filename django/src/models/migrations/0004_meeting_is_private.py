from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0003_add_authreg_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='is_private',
            field=models.BooleanField(default=False, help_text='Requiere autenticación en Jitsi'),
        ),
    ]
