# backend/company_slots/models/slots.py
from django.db import models
from django.core.validators import MinValueValidator
from common.models.mixins import TimestampedMixin

class CompanySlots(TimestampedMixin):
    """Gestion des slots par entreprise - Système de facturation à l'unité"""
    
    company = models.OneToOneField(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='slots',
        help_text="Entreprise propriétaire des slots"
    )
    
    # Slots configurés (payants)
    brands_slots = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text="Nombre de brands maximum autorisées"
    )
    users_slots = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Nombre d'utilisateurs maximum autorisés"
    )
    
    # Usage actuel (auto-calculé)
    current_brands_count = models.IntegerField(
        default=0,
        help_text="Nombre de brands actuellement créées"
    )
    current_users_count = models.IntegerField(
        default=0,
        help_text="Nombre d'utilisateurs actuellement créés"
    )
    
    # Métadonnées
    last_brands_count_update = models.DateTimeField(auto_now=True)
    last_users_count_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'company_slots'
        verbose_name = 'Company Slots'
        verbose_name_plural = 'Company Slots'
        indexes = [
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return f"Slots - {self.company.name} (B:{self.current_brands_count}/{self.brands_slots}, U:{self.current_users_count}/{self.users_slots})"
    
    def update_brands_count(self):
        """Met à jour le compteur de brands"""
        from brands_core.models.brand import Brand
        self.current_brands_count = Brand.objects.filter(
            company=self.company,
            is_deleted=False
        ).count()
        self.save(update_fields=['current_brands_count', 'last_brands_count_update'])
    
    def update_users_count(self):
        """Met à jour le compteur d'utilisateurs"""
        from users_core.models.user import CustomUser
        self.current_users_count = CustomUser.objects.filter(
            company=self.company,
            is_active=True
        ).count()
        self.save(update_fields=['current_users_count', 'last_users_count_update'])
    
    def get_brands_usage_percentage(self):
        """Pourcentage d'utilisation des slots brands"""
        if self.brands_slots == 0:
            return 0
        return round((self.current_brands_count / self.brands_slots) * 100, 2)
    
    def get_users_usage_percentage(self):
        """Pourcentage d'utilisation des slots users"""
        if self.users_slots == 0:
            return 0
        return round((self.current_users_count / self.users_slots) * 100, 2)
    
    def is_brands_limit_reached(self):
        """Vérifie si la limite de brands est atteinte"""
        return self.current_brands_count >= self.brands_slots
    
    def is_users_limit_reached(self):
        """Vérifie si la limite d'utilisateurs est atteinte"""
        return self.current_users_count >= self.users_slots

    def get_available_brands_slots(self):
        """Nombre de slots brands disponibles"""
        return max(0, self.brands_slots - self.current_brands_count)
    
    def get_available_users_slots(self):
        """Nombre de slots users disponibles"""
        return max(0, self.users_slots - self.current_users_count)