from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('jurisdiction_level', models.CharField(choices=[('national', 'National'), ('state', 'State'), ('local', 'Local')], max_length=32)),
                ('jurisdiction_name', models.CharField(blank=True, max_length=255)),
                ('source_type', models.CharField(choices=[('json', 'JSON'), ('csv', 'CSV'), ('geojson', 'GeoJSON'), ('api', 'API'), ('manual', 'Manual')], max_length=32)),
                ('homepage_url', models.URLField(blank=True)),
                ('download_url', models.URLField(blank=True)),
                ('license', models.CharField(blank=True, max_length=255)),
                ('refresh_strategy', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['jurisdiction_level', 'name']},
        ),
        migrations.CreateModel(
            name='ImportRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='running', max_length=32)),
                ('imported_count', models.PositiveIntegerField(default=0)),
                ('created_count', models.PositiveIntegerField(default=0)),
                ('updated_count', models.PositiveIntegerField(default=0)),
                ('failed_count', models.PositiveIntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('error_log', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('source_feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='import_runs', to='pages.sourcefeed')),
            ],
            options={'ordering': ['-started_at']},
        ),
        migrations.AddField(
            model_name='historicsite',
            name='source_feed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='pages.sourcefeed'),
        ),
    ]
