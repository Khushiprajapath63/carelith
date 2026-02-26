from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_add_encounter_to_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='created_at',
            field=models.DateTimeField(
                default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
