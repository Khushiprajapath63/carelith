from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_add_encounter_to_prescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='encounter',
            field=models.ForeignKey(
                to='records.encounter',
                on_delete=models.CASCADE,
                null=True,  # required for existing rows
            ),
        ),
    ]
