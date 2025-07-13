# backend/ai_templates_core/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('prompt_content', models.TextField(help_text='Contenu du prompt avec variables {{variable}}')),
                ('is_active', models.BooleanField(default=True)),
                ('is_public', models.BooleanField(default=False, help_text='Template partageable entre brands')),
            ],
            options={
                'db_table': 'base_template',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BrandTemplateConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('max_templates_per_type', models.PositiveIntegerField(default=50)),
                ('max_variables_per_template', models.PositiveIntegerField(default=20)),
                ('allow_custom_templates', models.BooleanField(default=True)),
                ('default_template_style', models.CharField(default='professional', max_length=100)),
            ],
            options={
                'db_table': 'brand_template_config',
            },
        ),
        migrations.CreateModel(
            name='TemplateType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'template_type',
                'ordering': ['name'],
            },
        ),
    ]
