# backend/ai_templates_storage/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateVariable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('display_name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('variable_type', models.CharField(choices=[('brand', 'Brand Data'), ('seo', 'SEO Data'), ('user', 'User Input'), ('system', 'System Generated')], default='user', max_length=50)),
                ('default_value', models.CharField(blank=True, max_length=500)),
                ('is_required', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'template_variable',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TemplateVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('version_number', models.PositiveIntegerField()),
                ('prompt_content', models.TextField()),
                ('changelog', models.TextField(blank=True, help_text='Description des changements')),
                ('is_current', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'template_version',
                'ordering': ['-version_number'],
            },
        ),
    ]
