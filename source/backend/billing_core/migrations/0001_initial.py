# backend/billing_core/migrations/0001_initial.py

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice_number', models.CharField(help_text='Numéro de facture', max_length=50, unique=True)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('open', 'Ouverte'), ('paid', 'Payée'), ('void', 'Annulée'), ('uncollectible', 'Irrécouvrable')], default='draft', help_text='Statut de la facture', max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, help_text='Sous-total', max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Montant des taxes', max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, help_text='Montant total', max_digits=10)),
                ('invoice_date', models.DateTimeField(help_text='Date de la facture')),
                ('due_date', models.DateTimeField(help_text="Date d'échéance")),
                ('paid_at', models.DateTimeField(blank=True, help_text='Date de paiement', null=True)),
                ('period_start', models.DateTimeField(help_text='Début de la période facturée')),
                ('period_end', models.DateTimeField(help_text='Fin de la période facturée')),
                ('stripe_invoice_id', models.CharField(blank=True, help_text='ID de la facture Stripe', max_length=255)),
            ],
            options={
                'db_table': 'invoice',
                'ordering': ['-invoice_date'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(help_text='Description de la ligne', max_length=255)),
                ('quantity', models.IntegerField(default=1, help_text='Quantité')),
                ('unit_price', models.DecimalField(decimal_places=2, help_text='Prix unitaire', max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, help_text='Prix total de la ligne', max_digits=10)),
                ('item_type', models.CharField(help_text='Type de ligne (plan, additional_brand, additional_user, etc.)', max_length=50)),
            ],
            options={
                'db_table': 'invoice_item',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Nom du plan', max_length=100, unique=True)),
                ('display_name', models.CharField(help_text="Nom d'affichage du plan", max_length=150)),
                ('description', models.TextField(blank=True, help_text='Description du plan')),
                ('plan_type', models.CharField(choices=[('starter', 'Starter'), ('professional', 'Professional'), ('enterprise', 'Enterprise'), ('custom', 'Custom')], help_text='Type de plan', max_length=20)),
                ('price', models.DecimalField(decimal_places=2, help_text='Prix du plan', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('billing_interval', models.CharField(choices=[('monthly', 'Mensuel'), ('yearly', 'Annuel'), ('one_time', 'Paiement unique')], default='monthly', help_text='Intervalle de facturation', max_length=20)),
                ('included_brands_slots', models.IntegerField(default=5, help_text='Nombre de slots brands inclus')),
                ('included_users_slots', models.IntegerField(default=10, help_text='Nombre de slots utilisateurs inclus')),
                ('additional_brand_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Prix par brand supplémentaire', max_digits=8)),
                ('additional_user_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Prix par utilisateur supplémentaire', max_digits=8)),
                ('is_active', models.BooleanField(default=True, help_text='Plan disponible pour souscription')),
                ('is_featured', models.BooleanField(default=False, help_text='Plan mis en avant')),
                ('stripe_price_id', models.CharField(blank=True, help_text='ID du prix Stripe', max_length=255)),
                ('sort_order', models.IntegerField(default=0, help_text="Ordre d'affichage")),
            ],
            options={
                'db_table': 'plan',
                'ordering': ['sort_order', 'price'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('active', 'Actif'), ('trialing', "Période d'essai"), ('past_due', 'Impayé'), ('canceled', 'Annulé'), ('unpaid', 'Non payé')], default='active', help_text="Statut de l'abonnement", max_length=20)),
                ('started_at', models.DateTimeField(help_text="Date de début de l'abonnement")),
                ('current_period_start', models.DateTimeField(help_text='Début de la période actuelle')),
                ('current_period_end', models.DateTimeField(help_text='Fin de la période actuelle')),
                ('trial_end', models.DateTimeField(blank=True, help_text="Fin de la période d'essai", null=True)),
                ('canceled_at', models.DateTimeField(blank=True, help_text="Date d'annulation", null=True)),
                ('amount', models.DecimalField(decimal_places=2, help_text="Montant de l'abonnement", max_digits=10)),
                ('stripe_subscription_id', models.CharField(blank=True, help_text="ID de l'abonnement Stripe", max_length=255)),
            ],
            options={
                'db_table': 'subscription',
            },
        ),
        migrations.CreateModel(
            name='UsageAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('alert_type', models.CharField(choices=[('brands_limit', 'Limite brands atteinte'), ('users_limit', 'Limite utilisateurs atteinte'), ('brands_warning', 'Avertissement brands (80%)'), ('users_warning', 'Avertissement utilisateurs (80%)')], help_text="Type d'alerte", max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('resolved', 'Résolue'), ('dismissed', 'Ignorée')], default='active', help_text="Statut de l'alerte", max_length=20)),
                ('message', models.TextField(help_text="Message de l'alerte")),
                ('triggered_at', models.DateTimeField(auto_now_add=True, help_text='Date de déclenchement')),
                ('resolved_at', models.DateTimeField(blank=True, help_text='Date de résolution', null=True)),
            ],
            options={
                'db_table': 'usage_alert',
                'ordering': ['-triggered_at'],
            },
        ),
    ]
