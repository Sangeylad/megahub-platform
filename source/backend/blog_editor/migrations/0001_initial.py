# backend/blog_editor/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog_content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_tiptap', models.JSONField(blank=True, help_text='Contenu TipTap JSON complet', null=True)),
                ('content_html', models.TextField(blank=True, help_text='Version HTML rendue depuis TipTap')),
                ('content_text', models.TextField(blank=True, help_text='Version texte pour recherche')),
                ('version', models.PositiveIntegerField(default=1)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='content', to='blog_content.blogarticle')),
            ],
            options={
                'verbose_name': 'Contenu Blog',
                'verbose_name_plural': 'Contenus Blog',
                'db_table': 'blog_editor_blogcontent',
            },
        ),
    ]
