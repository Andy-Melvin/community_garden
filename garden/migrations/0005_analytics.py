# Generated by Django 5.1.3 on 2024-11-18 00:17

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garden', '0004_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('SIGNUP', 'User Signup'), ('LOGIN', 'User Login'), ('PLOT_APPLICATION', 'Plot Application'), ('EVENT_SIGNUP', 'Event Signup'), ('CROP_RECORD', 'Crop Record Added')], max_length=50)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('details', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
