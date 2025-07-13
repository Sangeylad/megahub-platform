# backend/users_core/models/user.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models.mixins import TimestampedMixin

class CustomUser(AbstractUser, TimestampedMixin):
    """Utilisateur personnalisé avec support multi-tenant"""
    
    USER_TYPES = [
        ('agency_admin', 'Admin Agence'),
        ('brand_admin', 'Admin Marque'),
        ('brand_member', 'Membre Marque'),
        ('client_readonly', 'Client (Lecture seule)'),
    ]
    
    # Relations business
    company = models.ForeignKey(
        'company_core.Company',
        related_name='members',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Entreprise d'appartenance"
    )
    brands = models.ManyToManyField(
        'brands_core.Brand',
        related_name='users',
        blank=True,
        help_text="Marques accessibles par cet utilisateur"
    )
    
    # Type d'utilisateur
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default='brand_member',
        help_text="Type d'utilisateur définissant les permissions de base"
    )
    
    # Informations étendues
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Numéro de téléphone"
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Poste occupé"
    )
    
    # Permissions étendues pour dashboards clients
    can_access_analytics = models.BooleanField(
        default=False,
        help_text="Accès aux analytics (pour clients readonly)"
    )
    can_access_reports = models.BooleanField(
        default=False,
        help_text="Accès aux rapports (pour clients readonly)"
    )
    
    # Métadonnées
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dernière IP de connexion"
    )
    
    class Meta:
        db_table = 'custom_user'
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        """Override save pour mettre à jour le compteur de slots"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Mettre à jour le compteur d'utilisateurs de la company
        if is_new and self.company:
            from company_slots.models.slots import CompanySlots
            try:
                slots = self.company.slots
                slots.update_users_count()
            except CompanySlots.DoesNotExist:
                # Créer les slots si ils n'existent pas
                CompanySlots.objects.create(company=self.company)
    
    def delete(self, *args, **kwargs):
        """Override delete pour mettre à jour le compteur de slots"""
        company = self.company
        super().delete(*args, **kwargs)
        
        # Mettre à jour le compteur d'utilisateurs
        if company:
            from company_slots.models.slots import CompanySlots
            try:
                slots = company.slots
                slots.update_users_count()
            except CompanySlots.DoesNotExist:
                pass
    
    def is_company_admin(self):
        """Vérifie si l'utilisateur est admin de company"""
        return self.user_type == 'agency_admin' or (
            self.company and self.company.admin == self
        )
    
    def is_brand_admin(self):
        """Vérifie si l'utilisateur est admin d'au moins une brand"""
        return self.user_type == 'brand_admin' or self.administered_brands.exists()
    
    def can_invite_users(self):
        """Brand admin + Company admin peuvent inviter selon slots disponibles"""
        if not self.company:
            return False
            
        # Company admin OU Brand admin peuvent inviter
        if self.user_type in ['agency_admin', 'brand_admin']:
            return self.company.can_add_user()
            
        return False
    
    def get_accessible_brands(self):
        """Retourne les marques accessibles par cet utilisateur"""
        if self.is_company_admin():
            return self.company.brands.filter(is_deleted=False)
        return self.brands.filter(is_deleted=False)
    
    def get_administered_brands(self):
        """Retourne les marques administrées par cet utilisateur"""
        return self.administered_brands.filter(is_deleted=False)
    
    def can_access_brand(self, brand):
        """Vérifie si l'utilisateur peut accéder à une marque"""
        if self.is_company_admin():
            return brand.company == self.company
        return self.brands.filter(id=brand.id).exists()
    
    def can_admin_brand(self, brand):
        """Vérifie si l'utilisateur peut administrer une marque"""
        if self.is_company_admin():
            return brand.company == self.company
        return brand.brand_admin == self
    
    def get_permissions_summary(self):
        """Résumé des permissions pour l'interface"""
        return {
            'is_company_admin': self.is_company_admin(),
            'is_brand_admin': self.is_brand_admin(),
            'accessible_brands_count': self.get_accessible_brands().count(),
            'administered_brands_count': self.get_administered_brands().count(),
            'can_access_analytics': self.can_access_analytics,
            'can_access_reports': self.can_access_reports,
        }