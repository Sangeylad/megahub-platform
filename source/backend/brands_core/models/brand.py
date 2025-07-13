# backend/brands_core/models/brand.py
from django.db import models
from common.models.mixins import TimestampedMixin, SoftDeleteMixin

class Brand(TimestampedMixin, SoftDeleteMixin):
    """Modèle Brand de base - Marque client d'une agence"""
    
    # Relations
    company = models.ForeignKey(
        'company_core.Company',
        related_name='brands',
        on_delete=models.CASCADE,
        help_text="Entreprise propriétaire de la marque"
    )
    brand_admin = models.ForeignKey(
        'users_core.CustomUser',
        related_name='administered_brands',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Administrateur de la marque (unique par sécurité)"
    )
    
    # Informations de base
    name = models.CharField(
        max_length=255,
        help_text="Nom de la marque"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description de la marque"
    )
    url = models.URLField(
        max_length=255,
        default='http://example.com',
        help_text="Site web principal de la marque"
    )
    
    # Métadonnées
    is_active = models.BooleanField(
        default=True,
        help_text="Marque active"
    )
    
    class Meta:
        db_table = 'brand'
        ordering = ['name']
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['brand_admin']),
        ]
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.company.name})"
    
    def save(self, *args, **kwargs):
        """Override save pour mettre à jour le compteur de slots"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Mettre à jour le compteur de brands de la company
        if is_new:
            from company_slots.models.slots import CompanySlots
            try:
                slots = self.company.slots
                slots.update_brands_count()
            except CompanySlots.DoesNotExist:
                # Créer les slots si ils n'existent pas
                CompanySlots.objects.create(company=self.company)
    
    def delete(self, *args, **kwargs):
        """Override delete pour mettre à jour le compteur de slots"""
        company = self.company
        super().delete(*args, **kwargs)
        
        # Mettre à jour le compteur de brands
        from company_slots.models.slots import CompanySlots
        try:
            slots = company.slots
            slots.update_brands_count()
        except CompanySlots.DoesNotExist:
            pass
    
    def get_accessible_users(self):
        """Retourne les utilisateurs ayant accès à cette marque"""
        return self.users.filter(is_active=True)
    
    def has_user_access(self, user):
        """Vérifie si un utilisateur a accès à cette marque"""
        if not user.is_authenticated:
            return False
        
        # Company admin a accès à toutes les marques
        if hasattr(user, 'is_company_admin') and user.is_company_admin():
            return True
        
        # Brand admin
        if self.brand_admin == user:
            return True
        
        # Utilisateur avec accès explicite
        return self.users.filter(id=user.id).exists()
