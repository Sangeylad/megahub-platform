# /var/www/megahub/backend/crm_entities_core/models/account_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import CRMBaseMixin

class Account(CRMBaseMixin):
    """Entreprise cliente dans le CRM"""
    
    ACCOUNT_TYPES = [
        ('customer', 'Client'),
        ('prospect', 'Prospect'),
        ('partner', 'Partenaire'),
        ('vendor', 'Fournisseur'),
        ('competitor', 'Concurrent'),
    ]
    
    ACCOUNT_TIERS = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
        ('strategic', 'Stratégique'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('critical', 'Critique'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        help_text="Nom de l'entreprise"
    )
    account_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Numéro de compte auto-généré"
    )
    
    # Classification
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default='customer',
        help_text="Type de compte"
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Secteur d'activité (libre)"
    )
    company_category = models.ForeignKey(
        'company_categorization_core.IndustryCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Catégorie structurée"
    )
    
    # Informations entreprise
    website = models.URLField(blank=True, help_text="Site web")
    employee_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre d'employés"
    )
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Chiffre d'affaires annuel (€)"
    )
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    
    # Adresse facturation
    billing_street = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, default='France')
    
    # Adresse livraison
    shipping_street = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, default='France')
    
    # Hiérarchie
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_accounts',
        help_text="Compte parent"
    )
    account_hierarchy_level = models.IntegerField(
        default=1,
        help_text="Niveau dans la hiérarchie"
    )
    
    # Classification commerciale
    account_tier = models.CharField(
        max_length=20,
        choices=ACCOUNT_TIERS,
        default='standard',
        help_text="Niveau de compte"
    )
    customer_priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text="Priorité client"
    )
    
    # Conditions commerciales
    payment_terms = models.CharField(
        max_length=50,
        default='net_30',
        help_text="Conditions de paiement"
    )
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Limite de crédit (€)"
    )
    
    # Scoring et analytics
    health_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score santé client (0-100)"
    )
    engagement_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score engagement (0-100)"
    )
    ltv_predicted = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Lifetime Value prédite (€)"
    )
    churn_risk_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Score risque churn (0-1)"
    )
    
    # Dates importantes
    first_purchase_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date premier achat"
    )
    last_activity_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière activité"
    )
    next_renewal_date = models.DateField(
        null=True,
        blank=True,
        help_text="Prochaine date de renouvellement"
    )
    
    class Meta:
        db_table = 'crm_account'
        ordering = ['name']
        verbose_name = 'Compte CRM'
        verbose_name_plural = 'Comptes CRM'
        indexes = [
            models.Index(fields=['brand', 'account_type']),
            models.Index(fields=['name']),
            models.Index(fields=['account_number']),
            models.Index(fields=['customer_priority']),
            models.Index(fields=['health_score']),
            models.Index(fields=['parent_account']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            # Auto-générer le numéro de compte
            last_account = Account.objects.filter(
                brand=self.brand
            ).order_by('created_at').last()
            
            if last_account and last_account.account_number:
                try:
                    last_number = int(last_account.account_number.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            self.account_number = f"ACC-{new_number:06d}"
        
        super().save(*args, **kwargs)
    
    def get_full_address(self, address_type='billing'):
        """Retourne l'adresse complète formatée"""
        if address_type == 'billing':
            parts = [
                self.billing_street,
                f"{self.billing_postal_code} {self.billing_city}",
                self.billing_state,
                self.billing_country
            ]
        else:
            parts = [
                self.shipping_street,
                f"{self.shipping_postal_code} {self.shipping_city}",
                self.shipping_state,
                self.shipping_country
            ]
        
        return '\n'.join([part for part in parts if part.strip()])
    
    def update_health_score(self):
        """Recalcule le score santé basé sur différents facteurs"""
        # Logique de calcul du score santé
        # À implémenter selon les règles business
        pass
