# backend/glossary/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TermCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('slug', models.SlugField(max_length=120, unique=True, verbose_name='Slug URL')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('color', models.CharField(default='#6a5acd', help_text="Couleur hexadécimale pour l'UI", max_length=7, verbose_name='Couleur')),
                ('icon', models.CharField(blank=True, help_text="Classe CSS d'icône (ex: fas fa-bullhorn)", max_length=50, verbose_name='Icône')),
                ('order', models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('meta_title', models.CharField(blank=True, max_length=60, verbose_name='Meta Title')),
                ('meta_description', models.CharField(blank=True, max_length=160, verbose_name='Meta Description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='glossary.termcategory', verbose_name='Catégorie parente')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'verbose_name_plural': 'Catégories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=120, unique=True, verbose_name='Slug URL')),
                ('is_essential', models.BooleanField(default=False, help_text='Terme essentiel à connaître vs terme de niche', verbose_name='Essentiel')),
                ('difficulty_level', models.CharField(choices=[('beginner', 'Débutant'), ('intermediate', 'Intermédiaire'), ('advanced', 'Avancé'), ('expert', 'Expert')], default='intermediate', max_length=20, verbose_name='Niveau de difficulté')),
                ('popularity_score', models.PositiveIntegerField(default=0, help_text='Score de popularité basé sur les consultations', verbose_name='Score de popularité')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terms', to='glossary.termcategory', verbose_name='Catégorie')),
            ],
            options={
                'verbose_name': 'Terme',
                'verbose_name_plural': 'Termes',
                'ordering': ['-popularity_score', 'slug'],
            },
        ),
        migrations.CreateModel(
            name='TermTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('fr', 'Français'), ('en', 'English'), ('es', 'Español'), ('zh', '中文')], max_length=2, verbose_name='Langue')),
                ('context', models.CharField(blank=True, help_text="Contexte pour différencier (ex: 'sales' vs 'marketing')", max_length=50, verbose_name='Contexte')),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('definition', models.TextField(verbose_name='Définition')),
                ('examples', models.TextField(blank=True, help_text="Exemples concrets d'utilisation", verbose_name='Exemples')),
                ('formula', models.TextField(blank=True, help_text='Formule de calcul si applicable', verbose_name='Formule')),
                ('benchmarks', models.TextField(blank=True, help_text='Benchmarks et données de référence', verbose_name='Benchmarks')),
                ('sources', models.TextField(blank=True, help_text='Sources et références', verbose_name='Sources')),
                ('meta_title', models.CharField(blank=True, max_length=60, verbose_name='Meta Title')),
                ('meta_description', models.CharField(blank=True, max_length=160, verbose_name='Meta Description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='glossary.term', verbose_name='Terme')),
            ],
            options={
                'verbose_name': 'Traduction',
                'verbose_name_plural': 'Traductions',
                'ordering': ['language', 'context'],
                'unique_together': {('term', 'language', 'context')},
            },
        ),
        migrations.CreateModel(
            name='TermRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relation_type', models.CharField(choices=[('see_also', 'Voir aussi'), ('synonym', 'Synonyme'), ('antonym', 'Antonyme'), ('parent', 'Terme parent'), ('child', 'Terme enfant'), ('related', 'Lié')], max_length=20, verbose_name='Type de relation')),
                ('weight', models.PositiveIntegerField(default=1, help_text='Poids de la relation (1-10, plus élevé = plus important)', verbose_name='Poids')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations_from', to='glossary.term', verbose_name='Terme source')),
                ('to_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations_to', to='glossary.term', verbose_name='Terme cible')),
            ],
            options={
                'verbose_name': 'Relation entre termes',
                'verbose_name_plural': 'Relations entre termes',
                'unique_together': {('from_term', 'to_term', 'relation_type')},
            },
        ),
    ]
