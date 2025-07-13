# backend/company_core/migrations/0001_initial.py

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text="Nom de l'entreprise cliente", max_length=255)),
                ('billing_email', models.EmailField(help_text="Email de facturation (peut différer de l'admin)", max_length=254)),
                ('stripe_customer_id', models.CharField(blank=True, help_text='ID client Stripe pour la facturation', max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(default='http://example.com', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Entreprise active (peut utiliser la plateforme)')),
            ],
            options={
                'db_table': 'company',
                'ordering': ['name'],
            },
        ),
    ]
