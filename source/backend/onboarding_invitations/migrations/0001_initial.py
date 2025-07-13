# backend/onboarding_invitations/migrations/0001_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_core', '0003_company_trial_expires_at_and_more'),
        ('brands_core', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(help_text="Email de l'utilisateur invité", max_length=254)),
                ('token', models.UUIDField(default=uuid.uuid4, help_text="Token unique d'invitation", unique=True)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('accepted', 'Acceptée'), ('expired', 'Expirée'), ('cancelled', 'Annulée')], default='pending', help_text="Status de l'invitation", max_length=20)),
                ('user_type', models.CharField(choices=[('brand_member', 'Membre Marque'), ('brand_admin', 'Admin Marque')], default='brand_member', help_text="Type d'utilisateur à assigner", max_length=20)),
                ('expires_at', models.DateTimeField(help_text="Date d'expiration de l'invitation")),
                ('accepted_at', models.DateTimeField(blank=True, help_text="Date d'acceptation", null=True)),
                ('invitation_message', models.TextField(blank=True, help_text="Message personnalisé d'invitation")),
                ('accepted_by', models.ForeignKey(blank=True, help_text='User qui a accepté (une fois créé)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accepted_invitations', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(help_text='Company qui invite', on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='company_core.company')),
                ('invited_brand', models.ForeignKey(help_text="Brand spécifique d'invitation", on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='brands_core.brand')),
                ('invited_by', models.ForeignKey(help_text="User qui a envoyé l'invitation", on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_invitation',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['token'], name='user_invita_token_632fdb_idx'), models.Index(fields=['email', 'status'], name='user_invita_email_639fdb_idx'), models.Index(fields=['company', 'status'], name='user_invita_company_c08e25_idx'), models.Index(fields=['expires_at'], name='user_invita_expires_dc6b69_idx')],
                'unique_together': {('company', 'email', 'status')},
            },
        ),
    ]
