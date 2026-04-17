from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HistoricSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('summary', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=120)),
                ('state', models.CharField(blank=True, max_length=120)),
                ('category', models.CharField(choices=[
                    ('landmark', 'Landmark'),
                    ('marker', 'Historical Marker'),
                    ('museum', 'Museum'),
                    ('battlefield', 'Battlefield'),
                    ('memorial', 'Memorial'),
                    ('district', 'Historic District'),
                    ('other', 'Other'),
                ], default='other', max_length=32)),
                ('designation', models.CharField(blank=True, max_length=255)),
                ('era', models.CharField(blank=True, max_length=255)),
                ('source_name', models.CharField(blank=True, max_length=255)),
                ('source_id', models.CharField(blank=True, max_length=255)),
                ('wikipedia_url', models.URLField(blank=True)),
                ('reference_url', models.URLField(blank=True)),
                ('image_url', models.URLField(blank=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
