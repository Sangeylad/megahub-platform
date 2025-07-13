# backend/seo_keywords_cocoons/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seo_keywords_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CocoonCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('color', models.CharField(default='#3498db', help_text="Couleur hexadécimale pour l'interface", max_length=7)),
            ],
            options={
                'db_table': 'seo_keywords_cocoons_cocooncategory',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SemanticCocoon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=300, unique=True)),
                ('openai_file_id', models.CharField(blank=True, max_length=255, null=True)),
                ('openai_vector_store_id', models.CharField(blank=True, max_length=255, null=True)),
                ('openai_storage_type', models.CharField(choices=[('file', 'File'), ('vector_store', 'Vector Store')], default='vector_store', max_length=20)),
                ('openai_file_version', models.IntegerField(default=0)),
                ('last_pushed_at', models.DateTimeField(blank=True, null=True)),
                ('categories', models.ManyToManyField(blank=True, related_name='cocoons', to='seo_keywords_cocoons.cocooncategory')),
            ],
            options={
                'db_table': 'seo_keywords_cocoons_semanticcocoon',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CocoonKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cocoon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cocoon_keywords', to='seo_keywords_cocoons.semanticcocoon')),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cocoon_associations', to='seo_keywords_base.keyword')),
            ],
            options={
                'db_table': 'seo_keywords_cocoons_cocoonkeyword',
                'ordering': ['cocoon__name', '-keyword__volume'],
            },
        ),
        migrations.AddIndex(
            model_name='semanticcocoon',
            index=models.Index(fields=['name'], name='seo_keyword_name_791c48_idx'),
        ),
        migrations.AddIndex(
            model_name='semanticcocoon',
            index=models.Index(fields=['slug'], name='seo_keyword_slug_e39ad5_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='cocoonkeyword',
            unique_together={('cocoon', 'keyword')},
        ),
    ]
