# backend/ai_templates_categories/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='blue', help_text='Couleur Tailwind', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('usage_count', models.PositiveIntegerField(default=0, help_text="Nombre d'utilisations")),
            ],
            options={
                'db_table': 'template_tag',
                'ordering': ['-usage_count', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TemplateCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('display_name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('level', models.PositiveIntegerField(default=1, help_text='Niveau dans la hiérarchie (1-3)')),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('icon_name', models.CharField(blank=True, help_text='Nom icône Lucide', max_length=50)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='ai_templates_categories.templatecategory')),
            ],
            options={
                'db_table': 'template_category',
                'ordering': ['level', 'sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CategoryPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('permission_type', models.CharField(choices=[('view', 'Voir'), ('create', 'Créer'), ('edit', 'Modifier'), ('admin', 'Administration')], max_length=20)),
                ('required_plan', models.CharField(choices=[('free', 'Gratuit'), ('starter', 'Starter'), ('pro', 'Pro'), ('enterprise', 'Enterprise')], default='free', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='ai_templates_categories.templatecategory')),
            ],
            options={
                'db_table': 'category_permission',
            },
        ),
        migrations.AddIndex(
            model_name='templatecategory',
            index=models.Index(fields=['parent', 'is_active'], name='template_ca_parent__5f305d_idx'),
        ),
        migrations.AddIndex(
            model_name='templatecategory',
            index=models.Index(fields=['level', 'sort_order'], name='template_ca_level_529a5f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='templatecategory',
            unique_together={('parent', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='categorypermission',
            unique_together={('category', 'permission_type', 'required_plan')},
        ),
    ]
