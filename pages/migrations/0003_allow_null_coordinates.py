from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_phase2_ingestion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicsite',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='historicsite',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
