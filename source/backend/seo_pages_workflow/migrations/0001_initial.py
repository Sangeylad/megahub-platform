# backend/seo_pages_workflow/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PageScheduling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('scheduled_publish_date', models.DateTimeField(blank=True, help_text='Date/heure de publication programmée', null=True)),
                ('scheduled_unpublish_date', models.DateTimeField(blank=True, help_text='Date/heure de dépublication programmée', null=True)),
                ('auto_publish', models.BooleanField(default=False, help_text='Publication automatique à la date programmée')),
                ('notes', models.TextField(blank=True, help_text='Notes sur la programmation')),
            ],
            options={
                'verbose_name': 'Programmation de Page',
                'verbose_name_plural': 'Programmations de Page',
                'db_table': 'seo_pages_workflow_scheduling',
                'ordering': ['scheduled_publish_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PageStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('in_progress', 'En développement'), ('pending_review', 'En attente de review'), ('under_review', 'En cours de review'), ('changes_requested', 'Modifications demandées'), ('approved', 'Approuvé'), ('scheduled', 'Programmé'), ('published', 'Publié'), ('archived', 'Archivé'), ('deactivated', 'Désactivé')], default='draft', max_length=20)),
                ('status_changed_at', models.DateTimeField(auto_now_add=True)),
                ('production_notes', models.TextField(blank=True, help_text="Notes internes pour l'équipe")),
            ],
            options={
                'verbose_name': 'Statut de Page',
                'verbose_name_plural': 'Statuts de Page',
                'db_table': 'seo_pages_workflow_status',
                'ordering': ['-status_changed_at'],
            },
        ),
        migrations.CreateModel(
            name='PageWorkflowHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('old_status', models.CharField(max_length=20)),
                ('new_status', models.CharField(max_length=20)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Historique Workflow',
                'verbose_name_plural': 'Historiques Workflow',
                'db_table': 'seo_pages_workflow_history',
                'ordering': ['-created_at'],
            },
        ),
    ]
