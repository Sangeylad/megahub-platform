# backend/billing_stripe/models/stripe_models.py
from django.db import models
from common.models.mixins import TimestampedMixin
import json

class StripeCustomer(TimestampedMixin):
    """Synchronisation des données client Stripe"""
    
    company = models.OneToOneField(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='stripe_customer',
        help_text="Entreprise liée"
    )
    
    # Stripe data
    stripe_customer_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID client Stripe"
    )
    email = models.EmailField(
        help_text="Email du client Stripe"
    )
    
    # Metadata
    stripe_created_at = models.DateTimeField(
        help_text="Date de création côté Stripe"
    )
    last_sync_at = models.DateTimeField(
        auto_now=True,
        help_text="Dernière synchronisation"
    )
    
    # Raw data for debugging
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données brutes Stripe"
    )
    
    class Meta:
        db_table = 'stripe_customer'
        indexes = [
            models.Index(fields=['stripe_customer_id']),
        ]
    
    def __str__(self):
        return f"Stripe Customer: {self.company.name}"

class StripeSubscription(TimestampedMixin):
    """Synchronisation des abonnements Stripe"""
    
    subscription = models.OneToOneField(
        'billing_core.Subscription',
        on_delete=models.CASCADE,
        related_name='stripe_subscription',
        help_text="Abonnement local lié"
    )
    
    # Stripe data
    stripe_subscription_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID abonnement Stripe"
    )
    stripe_status = models.CharField(
        max_length=50,
        help_text="Statut Stripe"
    )
    
    # Dates (from Stripe)
    stripe_current_period_start = models.DateTimeField(
        help_text="Début période actuelle Stripe"
    )
    stripe_current_period_end = models.DateTimeField(
        help_text="Fin période actuelle Stripe"
    )
    stripe_trial_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fin d'essai Stripe"
    )
    
    # Sync metadata
    last_sync_at = models.DateTimeField(
        auto_now=True,
        help_text="Dernière synchronisation"
    )
    
    # Raw data for debugging
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données brutes Stripe"
    )
    
    class Meta:
        db_table = 'stripe_subscription'
        indexes = [
            models.Index(fields=['stripe_subscription_id']),
            models.Index(fields=['stripe_status']),
        ]
    
    def __str__(self):
        return f"Stripe Sub: {self.subscription.company.name}"

class StripeInvoice(TimestampedMixin):
    """Synchronisation des factures Stripe"""
    
    invoice = models.OneToOneField(
        'billing_core.Invoice',
        on_delete=models.CASCADE,
        related_name='stripe_invoice',
        help_text="Facture locale liée"
    )
    
    # Stripe data
    stripe_invoice_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID facture Stripe"
    )
    stripe_status = models.CharField(
        max_length=50,
        help_text="Statut Stripe"
    )
    
    # Amounts (from Stripe)
    stripe_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Sous-total Stripe"
    )
    stripe_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Taxes Stripe"
    )
    stripe_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total Stripe"
    )
    
    # Payment details
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID PaymentIntent Stripe"
    )
    stripe_charge_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID Charge Stripe"
    )
    
    # Dates
    stripe_created_at = models.DateTimeField(
        help_text="Date création Stripe"
    )
    stripe_paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date paiement Stripe"
    )
    
    # Sync metadata
    last_sync_at = models.DateTimeField(
        auto_now=True,
        help_text="Dernière synchronisation"
    )
    
    # Raw data for debugging
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données brutes Stripe"
    )
    
    class Meta:
        db_table = 'stripe_invoice'
        indexes = [
            models.Index(fields=['stripe_invoice_id']),
            models.Index(fields=['stripe_status']),
        ]
    
    def __str__(self):
        return f"Stripe Invoice: {self.invoice.invoice_number}"

class StripeWebhookEvent(TimestampedMixin):
    """Log des événements webhooks Stripe"""
    
    EVENT_TYPES = [
        ('customer.created', 'Client créé'),
        ('customer.updated', 'Client mis à jour'),
        ('customer.deleted', 'Client supprimé'),
        ('invoice.created', 'Facture créée'),
        ('invoice.payment_succeeded', 'Paiement réussi'),
        ('invoice.payment_failed', 'Paiement échoué'),
        ('customer.subscription.created', 'Abonnement créé'),
        ('customer.subscription.updated', 'Abonnement mis à jour'),
        ('customer.subscription.deleted', 'Abonnement supprimé'),
    ]
    
    PROCESSING_STATUS = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('processed', 'Traité'),
        ('failed', 'Échec'),
        ('ignored', 'Ignoré'),
    ]
    
    # Stripe event data
    stripe_event_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID événement Stripe"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        help_text="Type d'événement"
    )
    
    # Processing
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS,
        default='pending',
        help_text="Statut de traitement"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de traitement"
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text="Message d'erreur si échec"
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Nombre de tentatives"
    )
    
    # Raw event data
    raw_event_data = models.JSONField(
        help_text="Données brutes de l'événement"
    )
    
    class Meta:
        db_table = 'stripe_webhook_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stripe_event_id']),
            models.Index(fields=['event_type']),
            models.Index(fields=['processing_status']),
        ]
    
    def __str__(self):
        return f"Webhook: {self.event_type} - {self.get_processing_status_display()}"
    
    def mark_as_processed(self):
        """Marque l'événement comme traité"""
        from django.utils import timezone
        self.processing_status = 'processed'
        self.processed_at = timezone.now()
        self.save(update_fields=['processing_status', 'processed_at'])
    
    def mark_as_failed(self, error_message):
        """Marque l'événement comme échoué"""
        from django.utils import timezone
        self.processing_status = 'failed'
        self.processed_at = timezone.now()
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['processing_status', 'processed_at', 'error_message', 'retry_count'])
    
    def can_retry(self, max_retries=3):
        """Vérifie si l'événement peut être retraité"""
        return self.retry_count < max_retries and self.processing_status == 'failed'
    
    def get_event_data(self):
        """Retourne les données de l'événement parsées"""
        return self.raw_event_data.get('data', {}).get('object', {})

class StripePaymentMethod(TimestampedMixin):
    """Méthodes de paiement Stripe"""
    
    PAYMENT_TYPES = [
        ('card', 'Carte'),
        ('sepa_debit', 'Prélèvement SEPA'),
        ('paypal', 'PayPal'),
    ]
    
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='stripe_payment_methods',
        help_text="Entreprise propriétaire"
    )
    
    # Stripe data
    stripe_payment_method_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID méthode de paiement Stripe"
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        help_text="Type de paiement"
    )
    
    # Card details (if applicable)
    card_brand = models.CharField(
        max_length=20,
        blank=True,
        help_text="Marque de carte"
    )
    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        help_text="4 derniers chiffres"
    )
    card_exp_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Mois d'expiration"
    )
    card_exp_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Année d'expiration"
    )
    
    # Status
    is_default = models.BooleanField(
        default=False,
        help_text="Méthode de paiement par défaut"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Méthode de paiement active"
    )
    
    # Raw data
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données brutes Stripe"
    )
    
    class Meta:
        db_table = 'stripe_payment_method'
        indexes = [
            models.Index(fields=['stripe_payment_method_id']),
            models.Index(fields=['company', 'is_default']),
        ]
    
    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.card_brand} ****{self.card_last4}"
        return f"{self.get_payment_type_display()}"
    
    def get_display_name(self):
        """Nom d'affichage pour l'interface"""
        if self.payment_type == 'card':
            return f"{self.card_brand.title()} se terminant par {self.card_last4}"
        return self.get_payment_type_display()
    
    def is_card_expired(self):
        """Vérifie si la carte est expirée"""
        if self.payment_type != 'card' or not self.card_exp_month or not self.card_exp_year:
            return False
        
        from datetime import datetime
        now = datetime.now()
        return (self.card_exp_year < now.year or 
                (self.card_exp_year == now.year and self.card_exp_month < now.month))
