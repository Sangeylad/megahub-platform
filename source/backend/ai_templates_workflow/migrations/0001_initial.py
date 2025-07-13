# backend/ai_templates_workflow/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai_templates_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('pending_review', 'En attente de review'), ('approved', 'Approuvé'), ('rejected', 'Rejeté'), ('published', 'Publié')], default='draft', max_length=20)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'template_approval',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplateReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField()),
                ('rating', models.PositiveIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True)),
                ('review_type', models.CharField(choices=[('comment', 'Commentaire'), ('suggestion', 'Suggestion'), ('approval', 'Approbation'), ('rejection', 'Rejet')], max_length=20)),
            ],
            options={
                'db_table': 'template_review',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplateValidationRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('rule_type', models.CharField(choices=[('security', 'Sécurité'), ('quality', 'Qualité'), ('format', 'Format'), ('content', 'Contenu')], max_length=50)),
                ('validation_function', models.CharField(help_text='Nom de la fonction de validation', max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('is_blocking', models.BooleanField(default=False, help_text='Bloque la publication si échec')),
                ('error_message', models.TextField(help_text="Message d'erreur si validation échoue")),
            ],
            options={
                'db_table': 'template_validation_rule',
                'ordering': ['rule_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TemplateValidationResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField()),
                ('error_details', models.TextField(blank=True)),
                ('validation_data', models.JSONField(default=dict, help_text='Données techniques de la validation')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='validation_results', to='ai_templates_core.basetemplate')),
            ],
            options={
                'db_table': 'template_validation_result',
                'ordering': ['-created_at'],
            },
        ),
    ]
