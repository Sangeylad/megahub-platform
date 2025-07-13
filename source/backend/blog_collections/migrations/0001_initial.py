# backend/blog_collections/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('collection_type', models.CharField(choices=[('dossier', 'Dossier Thématique'), ('serie', "Série d'Articles"), ('formation', 'Formation'), ('guide', 'Guide Complet'), ('newsletter', 'Série Newsletter')], default='dossier', max_length=20)),
                ('cover_image_url', models.URLField(blank=True, help_text='Image de couverture de la collection')),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False, help_text='Collection mise en avant')),
                ('is_sequential', models.BooleanField(default=True, help_text='Lecture séquentielle recommandée')),
                ('meta_title', models.CharField(blank=True, max_length=60)),
                ('meta_description', models.CharField(blank=True, max_length=160)),
            ],
            options={
                'verbose_name': 'Collection Blog',
                'verbose_name_plural': 'Collections Blog',
                'db_table': 'blog_collections_blogcollection',
                'ordering': ['-is_featured', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BlogCollectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Ordre dans la collection')),
                ('custom_title', models.CharField(blank=True, help_text='Titre personnalisé dans cette collection', max_length=200)),
                ('custom_description', models.TextField(blank=True, help_text='Description personnalisée')),
                ('is_optional', models.BooleanField(default=False, help_text='Article optionnel dans le parcours')),
                ('is_bonus', models.BooleanField(default=False, help_text='Contenu bonus')),
            ],
            options={
                'verbose_name': 'Article Collection',
                'verbose_name_plural': 'Articles Collection',
                'db_table': 'blog_collections_blogcollectionitem',
                'ordering': ['order'],
            },
        ),
    ]
