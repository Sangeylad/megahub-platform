# backend/blog_publishing/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog_content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPublishingStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('pending_review', 'En attente de relecture'), ('approved', 'Approuvé'), ('scheduled', 'Programmé'), ('published', 'Publié'), ('unpublished', 'Dépublié'), ('archived', 'Archivé')], default='draft', max_length=20)),
                ('published_date', models.DateTimeField(blank=True, help_text='Date de publication publique', null=True)),
                ('scheduled_date', models.DateTimeField(blank=True, help_text='Date de publication programmée', null=True)),
                ('last_published_date', models.DateTimeField(blank=True, help_text='Dernière publication (historique)', null=True)),
                ('submitted_for_review_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('is_featured', models.BooleanField(default=False, help_text='Article mis en avant')),
                ('is_premium', models.BooleanField(default=False, help_text='Contenu premium')),
                ('is_evergreen', models.BooleanField(default=False, help_text='Contenu intemporel')),
                ('notify_on_publish', models.BooleanField(default=True, help_text='Notifier lors de la publication')),
            ],
            options={
                'verbose_name': 'Statut Publication',
                'verbose_name_plural': 'Statuts Publication',
                'db_table': 'blog_publishing_blogpublishingstatus',
            },
        ),
        migrations.CreateModel(
            name='BlogScheduledPublication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('scheduled_for', models.DateTimeField(help_text='Date/heure de publication programmée')),
                ('execution_status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En cours'), ('completed', 'Terminée'), ('failed', 'Échec'), ('cancelled', 'Annulée')], default='pending', max_length=20)),
                ('executed_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('max_retries', models.PositiveIntegerField(default=3)),
                ('notify_author', models.BooleanField(default=True)),
                ('update_social_media', models.BooleanField(default=False)),
                ('send_newsletter', models.BooleanField(default=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_publications', to='blog_content.blogarticle')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
