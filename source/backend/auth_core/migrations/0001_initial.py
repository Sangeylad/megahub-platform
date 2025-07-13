# backend/auth_core/migrations/0001_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(help_text='Email de tentative de connexion', max_length=254)),
                ('ip_address', models.GenericIPAddressField(help_text='Adresse IP de la tentative')),
                ('success', models.BooleanField(default=False, help_text='Tentative réussie ou non')),
                ('user_agent', models.TextField(blank=True, help_text='User agent du navigateur')),
                ('failure_reason', models.CharField(blank=True, help_text="Raison de l'échec si applicable", max_length=100)),
            ],
            options={
                'db_table': 'auth_login_attempt',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['email', 'created_at'], name='auth_login__email_a1c1df_idx'), models.Index(fields=['ip_address', 'created_at'], name='auth_login__ip_addr_b3ce76_idx')],
            },
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('token', models.CharField(help_text='Token de réinitialisation', max_length=64, unique=True)),
                ('expires_at', models.DateTimeField(help_text="Date d'expiration du token")),
                ('used', models.BooleanField(default=False, help_text='Token utilisé ou non')),
                ('user', models.ForeignKey(help_text='Utilisateur concerné', on_delete=django.db.models.deletion.CASCADE, related_name='password_reset_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'auth_password_reset_token',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['token'], name='auth_passwo_token_ceb1cb_idx'), models.Index(fields=['user', 'used'], name='auth_passwo_user_id_cbdb24_idx')],
            },
        ),
    ]
