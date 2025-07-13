# backend/users_roles/migrations/0001_initial.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company_features', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_core', '0001_initial'),
        ('brands_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Nom unique de la permission', max_length=100, unique=True)),
                ('display_name', models.CharField(help_text="Nom d'affichage de la permission", max_length=150)),
                ('description', models.TextField(blank=True, help_text='Description de la permission')),
                ('permission_type', models.CharField(choices=[('read', 'Lecture'), ('write', 'Écriture'), ('delete', 'Suppression'), ('admin', 'Administration')], help_text='Type de permission', max_length=20)),
                ('resource_type', models.CharField(help_text='Type de ressource (model, feature, etc.)', max_length=50)),
                ('is_active', models.BooleanField(default=True, help_text='Permission active')),
            ],
            options={
                'db_table': 'permission',
                'ordering': ['resource_type', 'permission_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Nom unique du rôle', max_length=50, unique=True)),
                ('display_name', models.CharField(help_text="Nom d'affichage du rôle", max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description détaillée du rôle')),
                ('role_type', models.CharField(choices=[('system', 'Système'), ('company', 'Entreprise'), ('brand', 'Marque'), ('feature', 'Feature')], default='brand', help_text='Type de rôle', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Rôle actif')),
                ('is_system', models.BooleanField(default=False, help_text='Rôle système (non supprimable)')),
            ],
            options={
                'db_table': 'role',
                'ordering': ['role_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('granted_at', models.DateTimeField(auto_now_add=True, help_text="Date d'attribution du rôle")),
                ('expires_at', models.DateTimeField(blank=True, help_text="Date d'expiration du rôle", null=True)),
                ('brand', models.ForeignKey(blank=True, help_text='Contexte marque (optionnel)', null=True, on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
                ('company', models.ForeignKey(blank=True, help_text='Contexte entreprise (optionnel)', null=True, on_delete=django.db.models.deletion.CASCADE, to='company_core.company')),
                ('feature', models.ForeignKey(blank=True, help_text='Contexte feature (optionnel)', null=True, on_delete=django.db.models.deletion.CASCADE, to='company_features.feature')),
                ('granted_by', models.ForeignKey(blank=True, help_text='Utilisateur qui a accordé ce rôle', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_roles', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(help_text='Rôle assigné', on_delete=django.db.models.deletion.CASCADE, related_name='user_assignments', to='users_roles.role')),
                ('user', models.ForeignKey(help_text='Utilisateur', on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_role',
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_granted', models.BooleanField(default=True, help_text='Permission accordée (False = refusée explicitement)')),
                ('permission', models.ForeignKey(help_text='Permission', on_delete=django.db.models.deletion.CASCADE, related_name='permission_roles', to='users_roles.permission')),
                ('role', models.ForeignKey(help_text='Rôle', on_delete=django.db.models.deletion.CASCADE, related_name='role_permissions', to='users_roles.role')),
            ],
            options={
                'db_table': 'role_permission',
            },
        ),
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['is_active'], name='role_is_acti_d578e4_idx'),
        ),
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['role_type'], name='role_role_ty_629a78_idx'),
        ),
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['is_active'], name='permission_is_acti_50c675_idx'),
        ),
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['resource_type'], name='permission_resourc_b75563_idx'),
        ),
        migrations.AddIndex(
            model_name='userrole',
            index=models.Index(fields=['user', 'role'], name='user_role_user_id_1d88a5_idx'),
        ),
        migrations.AddIndex(
            model_name='userrole',
            index=models.Index(fields=['expires_at'], name='user_role_expires_8ea876_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together={('user', 'role', 'company', 'brand', 'feature')},
        ),
        migrations.AddIndex(
            model_name='rolepermission',
            index=models.Index(fields=['role', 'is_granted'], name='role_permis_role_id_0105d0_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='rolepermission',
            unique_together={('role', 'permission')},
        ),
    ]
