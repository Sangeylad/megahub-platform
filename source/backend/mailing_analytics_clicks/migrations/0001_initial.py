# Generated by Django 4.2.23 on 2025-07-26 20:35

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailClick',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('clicked_url', models.URLField()),
                ('original_url', models.URLField()),
                ('link_text', models.CharField(blank=True, max_length=255)),
                ('link_position', models.CharField(blank=True, max_length=50)),
                ('is_unique', models.BooleanField(default=True)),
                ('click_count', models.IntegerField(default=1)),
                ('device_type', models.CharField(blank=True, max_length=30)),
                ('referrer', models.URLField(blank=True)),
            ],
        ),
    ]
