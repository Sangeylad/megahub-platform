# backend/seo_pages_keywords/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_pages_content', '0001_initial'),
        ('seo_keywords_cocoons', '0001_initial'),
        ('seo_keywords_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('keyword_type', models.CharField(choices=[('primary', 'Primaire'), ('secondary', 'Secondaire'), ('anchor', 'Ancre')], default='secondary', max_length=20)),
                ('is_ai_selected', models.BooleanField(default=False, help_text="Mot-clé sélectionné automatiquement par l'IA")),
                ('notes', models.TextField(blank=True, null=True)),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_associations', to='seo_keywords_base.keyword')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_keywords', to='seo_pages_content.page')),
                ('source_cocoon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='page_keyword_associations', to='seo_keywords_cocoons.semanticcocoon')),
            ],
            options={
                'verbose_name': 'Association Page-Mot clé',
                'verbose_name_plural': 'Associations Page-Mot clé',
                'db_table': 'seo_pages_keywords_association',
                'ordering': ['page', 'keyword_type', 'position'],
                'indexes': [models.Index(fields=['page', 'keyword_type'], name='seo_pages_k_page_id_9f5fb6_idx'), models.Index(fields=['keyword_type', 'is_ai_selected'], name='seo_pages_k_keyword_83495b_idx'), models.Index(fields=['source_cocoon'], name='seo_pages_k_source__e93602_idx')],
                'unique_together': {('page', 'keyword')},
            },
        ),
    ]
