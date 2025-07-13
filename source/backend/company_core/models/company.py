# backend/company_core/models/company.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from common.models.mixins import TimestampedMixin, SoftDeleteMixin

class Company(TimestampedMixin, SoftDeleteMixin):
    """Modèle Company de base - Entité principale de facturation"""
    
    name = models.CharField(max_length=255, help_text="Nom de l'entreprise cliente")
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='admin_company',
        on_delete=models.CASCADE,
        help_text="Administrateur principal de l'entreprise"
    )
    
    # Billing essentials
    billing_email = models.EmailField(
        help_text="Email de facturation (peut différer de l'admin)"
    )
    stripe_customer_id = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="ID client Stripe pour la facturation"
    )
    
    # Business info
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=255, default='http://example.com')
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Entreprise active (peut utiliser la plateforme)"
    )
    
    # 🆕 TRIAL SYSTEM
    trial_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'expiration du trial (2 semaines)"
    )
    
    class Meta:
        db_table = 'company'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['trial_expires_at']),  # 🆕 Index pour trial
        ]
    
    def __str__(self):
        return self.name
    
    def can_add_brand(self):
        """Vérifie si l'entreprise peut ajouter une brand"""
        from company_slots.models.slots import CompanySlots
        try:
            slots = self.slots
            return slots.current_brands_count < slots.brands_slots
        except CompanySlots.DoesNotExist:
            return False
    
    def can_add_user(self):
        """Vérifie si l'entreprise peut ajouter un utilisateur"""
        from company_slots.models.slots import CompanySlots
        try:
            slots = self.slots
            return slots.current_users_count < slots.users_slots
        except CompanySlots.DoesNotExist:
            return False
    
    # 🆕 TRIAL METHODS
    def is_in_trial(self):
        """Vérifie si la company est en période d'essai"""
        if not self.trial_expires_at:
            return False
        return timezone.now() <= self.trial_expires_at
    
    def trial_days_remaining(self):
        """Nombre de jours restants dans le trial"""
        if not self.is_in_trial():
            return 0
        remaining = self.trial_expires_at - timezone.now()
        return remaining.days
    
    # 🆕 BUSINESS MODE DETECTION
    def is_solo_business(self):
        """Détecte si c'est un business solo (1 brand exactement)"""
        return self.brands.filter(is_deleted=False).count() == 1
    
    def is_agency(self):
        """Détecte si c'est une agence (2+ brands)"""
        return self.brands.filter(is_deleted=False).count() >= 2
    
    def get_business_mode(self):
        """Retourne le mode business actuel"""
        if self.is_solo_business():
            return 'solo'
        elif self.is_agency():
            return 'agency'
        else:
            return 'empty'  # Aucune brand active
    
    # 🆕 ENHANCED STATS
    def get_stats_summary(self):
        """Résumé des statistiques company"""
        from company_slots.models.slots import CompanySlots
        
        try:
            slots = self.slots
            brands_count = self.brands.filter(is_deleted=False).count()
            users_count = self.members.filter(is_active=True).count()
            
            return {
                'business_mode': self.get_business_mode(),
                'is_in_trial': self.is_in_trial(),
                'trial_days_remaining': self.trial_days_remaining(),
                'brands': {
                    'current': brands_count,
                    'limit': slots.brands_slots,
                    'can_add': self.can_add_brand()
                },
                'users': {
                    'current': users_count,
                    'limit': slots.users_slots,
                    'can_add': self.can_add_user()
                }
            }
        except CompanySlots.DoesNotExist:
            return {
                'business_mode': self.get_business_mode(),
                'is_in_trial': self.is_in_trial(),
                'trial_days_remaining': self.trial_days_remaining(),
                'error': 'CompanySlots not found'
            }