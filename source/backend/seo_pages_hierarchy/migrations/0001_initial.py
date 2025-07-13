# backend/seo_pages_hierarchy/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageHierarchy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hierarchy', to='seo_pages_content.page')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_hierarchy', to='seo_pages_content.page')),
            ],
            options={
                'verbose_name': 'Hiérarchie de Page',
                'verbose_name_plural': 'Hiérarchies de Page',
                'db_table': 'seo_pages_hierarchy_hierarchy',
                'ordering': ['page', '-created_at'],
                'indexes': [models.Index(fields=['page', 'parent'], name='seo_pages_h_page_id_f71b9b_idx')],
            },
        ),
        migrations.CreateModel(
            name='PageBreadcrumb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('breadcrumb_json', models.JSONField(default=list, help_text="Cache JSON du fil d'Ariane")),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='breadcrumb_cache', to='seo_pages_content.page')),
            ],
            options={
                'verbose_name': "Fil d'Ariane",
                'verbose_name_plural': "Fils d'Ariane",
                'db_table': 'seo_pages_hierarchy_breadcrumb',
                'ordering': ['page', '-updated_at'],
                'indexes': [models.Index(fields=['page'], name='seo_pages_h_page_id_5240d6_idx')],
            },
        ),
    ]
