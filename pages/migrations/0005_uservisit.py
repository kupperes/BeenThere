from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0004_alter_historicsite_id_alter_importrun_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visited_at', models.DateTimeField(auto_now_add=True)),
                ('historic_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_visits', to='pages.historicsite')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_visits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-visited_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='uservisit',
            constraint=models.UniqueConstraint(fields=('user', 'historic_site'), name='unique_user_site_visit'),
        ),
    ]
