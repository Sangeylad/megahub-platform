# backend/billing_core/models/billing.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from common.models.mixins import TimestampedMixin

class Plan(TimestampedMixin):
    """Plans de facturation disponibles"""
    
    PLAN_TYPES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Custom'),
    ]
    
    BILLING_INTERVALS = [
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
        ('one_time', 'Paiement unique'),
    ]
    
    # Plan basics
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom du plan"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Nom d'affichage du plan"
    )
    description = models.TextField(
        blank=True,
        help_text="Description du plan"
    )
    
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPES,
        help_text="Type de plan"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Prix du plan"
    )
    billing_interval = models.CharField(
        max_length=20,
        choices=BILLING_INTERVALS,
        default='monthly',
        help_text="Intervalle de facturation"
    )
    
    # Slots inclus
    included_brands_slots = models.IntegerField(
        default=5,
        help_text="Nombre de slots brands inclus"
    )
    included_users_slots = models.IntegerField(
        default=10,
        help_text="Nombre de slots utilisateurs inclus"
    )
    
    # Pricing additionnels
    additional_brand_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Prix par brand supplémentaire"
    )
    additional_user_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Prix par utilisateur supplémentaire"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Plan disponible pour souscription"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Plan mis en avant"
    )
    
    # Stripe integration
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID du prix Stripe"
    )
    
    # Ordering
    sort_order = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage"
    )
    
    class Meta:
        db_table = 'plan'
        ordering = ['sort_order', 'price']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['plan_type']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.get_billing_interval_display()})"
    
    def get_total_price_for_slots(self, brands_slots, users_slots):
        """Calcule le prix total pour un nombre de slots donné"""
        additional_brands = max(0, brands_slots - self.included_brands_slots)
        additional_users = max(0, users_slots - self.included_users_slots)
        
        additional_cost = (
            (additional_brands * self.additional_brand_price) +
            (additional_users * self.additional_user_price)
        )
        
        return self.price + additional_cost
    
    def get_features_summary(self):
        """Résumé des features pour l'affichage"""
        return {
            'brands_slots': self.included_brands_slots,
            'users_slots': self.included_users_slots,
            'additional_brand_price': self.additional_brand_price,
            'additional_user_price': self.additional_user_price,
            'billing_interval': self.get_billing_interval_display(),
        }

class Subscription(TimestampedMixin):
    """Abonnement d'une entreprise à un plan"""
    
    SUBSCRIPTION_STATUS = [
        ('active', 'Actif'),
        ('trialing', 'Période d\'essai'),
        ('past_due', 'Impayé'),
        ('canceled', 'Annulé'),
        ('unpaid', 'Non payé'),
    ]
    
    # Relations
    company = models.OneToOneField(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='subscription',
        help_text="Entreprise abonnée"
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        help_text="Plan souscrit"
    )
    
    # Subscription details
    status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS,
        default='active',
        help_text="Statut de l'abonnement"
    )
    
    # Dates
    started_at = models.DateTimeField(
        help_text="Date de début de l'abonnement"
    )
    current_period_start = models.DateTimeField(
        help_text="Début de la période actuelle"
    )
    current_period_end = models.DateTimeField(
        help_text="Fin de la période actuelle"
    )
    trial_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fin de la période d'essai"
    )
    canceled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'annulation"
    )
    
    # Billing
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Montant de l'abonnement"
    )
    
    # Stripe integration
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID de l'abonnement Stripe"
    )
    
    class Meta:
        db_table = 'subscription'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['current_period_end']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.display_name} ({self.get_status_display()})"
    
    def is_active(self):
        """Vérifie si l'abonnement est actif"""
        return self.status in ['active', 'trialing']
    
    def is_trial(self):
        """Vérifie si l'abonnement est en période d'essai"""
        if not self.trial_end:
            return False
        from django.utils import timezone
        return timezone.now() <= self.trial_end
    
    def days_until_renewal(self):
        """Nombre de jours avant le renouvellement"""
        from django.utils import timezone
        delta = self.current_period_end - timezone.now()
        return delta.days if delta.days > 0 else 0
    
    def get_usage_summary(self):
        """Résumé de l'utilisation pour la facturation"""
        try:
            slots = self.company.slots
            return {
                'brands_used': slots.current_brands_count,
                'users_used': slots.current_users_count,
                'brands_included': self.plan.included_brands_slots,
                'users_included': self.plan.included_users_slots,
                'additional_brands': max(0, slots.current_brands_count - self.plan.included_brands_slots),
                'additional_users': max(0, slots.current_users_count - self.plan.included_users_slots),
            }
        except:
            return {}

class Invoice(TimestampedMixin):
    """Factures générées"""
    
    INVOICE_STATUS = [
        ('draft', 'Brouillon'),
        ('open', 'Ouverte'),
        ('paid', 'Payée'),
        ('void', 'Annulée'),
        ('uncollectible', 'Irrécouvrable'),
    ]
    
    # Relations
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text="Entreprise facturée"
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text="Abonnement facturé"
    )
    
    # Invoice details
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Numéro de facture"
    )
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS,
        default='draft',
        help_text="Statut de la facture"
    )
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Sous-total"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Montant des taxes"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Montant total"
    )
    
    # Dates
    invoice_date = models.DateTimeField(
        help_text="Date de la facture"
    )
    due_date = models.DateTimeField(
        help_text="Date d'échéance"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de paiement"
    )
    
    # Period
    period_start = models.DateTimeField(
        help_text="Début de la période facturée"
    )
    period_end = models.DateTimeField(
        help_text="Fin de la période facturée"
    )
    
    # Stripe integration
    stripe_invoice_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID de la facture Stripe"
    )
    
    class Meta:
        db_table = 'invoice'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Facture {self.invoice_number} - {self.company.name}"
    
    def is_overdue(self):
        """Vérifie si la facture est en retard"""
        if self.status == 'paid':
            return False
        from django.utils import timezone
        return timezone.now() > self.due_date
    
    def days_overdue(self):
        """Nombre de jours de retard"""
        if not self.is_overdue():
            return 0
        from django.utils import timezone
        delta = timezone.now() - self.due_date
        return delta.days

class InvoiceItem(TimestampedMixin):
    """Lignes de facture"""
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Facture"
    )
    
    # Item details
    description = models.CharField(
        max_length=255,
        help_text="Description de la ligne"
    )
    quantity = models.IntegerField(
        default=1,
        help_text="Quantité"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix unitaire"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix total de la ligne"
    )
    
    # Metadata
    item_type = models.CharField(
        max_length=50,
        help_text="Type de ligne (plan, additional_brand, additional_user, etc.)"
    )
    
    class Meta:
        db_table = 'invoice_item'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.description} - {self.total_price}€"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement le prix total"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class UsageAlert(TimestampedMixin):
    """Alertes d'utilisation pour prévenir les dépassements"""
    
    ALERT_TYPES = [
        ('brands_limit', 'Limite brands atteinte'),
        ('users_limit', 'Limite utilisateurs atteinte'),
        ('brands_warning', 'Avertissement brands (80%)'),
        ('users_warning', 'Avertissement utilisateurs (80%)'),
    ]
    
    ALERT_STATUS = [
        ('active', 'Active'),
        ('resolved', 'Résolue'),
        ('dismissed', 'Ignorée'),
    ]
    
    # Relations
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='usage_alerts',
        help_text="Entreprise concernée"
    )
    
    # Alert details
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        help_text="Type d'alerte"
    )
    status = models.CharField(
        max_length=20,
        choices=ALERT_STATUS,
        default='active',
        help_text="Statut de l'alerte"
    )
    
    message = models.TextField(
        help_text="Message de l'alerte"
    )
    
    # Metadata
    triggered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de déclenchement"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de résolution"
    )
    
    class Meta:
        db_table = 'usage_alert'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['alert_type']),
        ]
    
    def __str__(self):
        return f"[{self.get_alert_type_display()}] {self.company.name}"
    
    def resolve(self):
        """Marque l'alerte comme résolue"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at'])
    
    def dismiss(self):
        """Marque l'alerte comme ignorée"""
        from django.utils import timezone
        self.status = 'dismissed'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at'])
