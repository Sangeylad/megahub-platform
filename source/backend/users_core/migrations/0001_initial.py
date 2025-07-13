# backend/users_core/migrations/0001_initial.py

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company_core', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_type', models.CharField(choices=[('agency_admin', 'Admin Agence'), ('brand_admin', 'Admin Marque'), ('brand_member', 'Membre Marque'), ('client_readonly', 'Client (Lecture seule)')], default='brand_member', help_text="Type d'utilisateur définissant les permissions de base", max_length=20)),
                ('phone', models.CharField(blank=True, help_text='Numéro de téléphone', max_length=20)),
                ('position', models.CharField(blank=True, help_text='Poste occupé', max_length=100)),
                ('can_access_analytics', models.BooleanField(default=False, help_text='Accès aux analytics (pour clients readonly)')),
                ('can_access_reports', models.BooleanField(default=False, help_text='Accès aux rapports (pour clients readonly)')),
                ('last_login_ip', models.GenericIPAddressField(blank=True, help_text='Dernière IP de connexion', null=True)),
                ('brands', models.ManyToManyField(blank=True, help_text='Marques accessibles par cet utilisateur', related_name='users', to='brands_core.brand')),
                ('company', models.ForeignKey(blank=True, help_text="Entreprise d'appartenance", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='company_core.company')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'custom_user',
                'indexes': [models.Index(fields=['company', 'is_active'], name='custom_user_company_21afae_idx'), models.Index(fields=['user_type'], name='custom_user_user_ty_dbe6e2_idx')],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
