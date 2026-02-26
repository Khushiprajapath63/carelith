from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='encounter',
            field=models.ForeignKey(
                to='records.encounter',
                on_delete=models.CASCADE,
                null=True,
            ),
        ),
    ]
