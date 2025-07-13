# backend/brands_core/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Nom de la marque', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description de la marque', null=True)),
                ('url', models.URLField(default='http://example.com', help_text='Site web principal de la marque', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Marque active')),
            ],
            options={
                'db_table': 'brand',
                'ordering': ['name'],
            },
        ),
    ]
