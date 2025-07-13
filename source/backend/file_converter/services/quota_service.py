# backend/file_converter/services/quota_service.py

import logging
from datetime import timedelta
from django.utils import timezone
from ..models import ConversionQuota

logger = logging.getLogger(__name__)

class QuotaService:
    """Service de gestion des quotas de conversion"""
    
    def __init__(self):
        self.default_monthly_limit = 100
        self.default_max_file_size = 50 * 1024 * 1024  # 50MB
    
    def get_or_create_quota(self, brand):
        """Récupère ou crée le quota pour une brand"""
        quota, created = ConversionQuota.objects.get_or_create(
            brand=brand,
            defaults={
                'monthly_limit': self.default_monthly_limit,
                'current_month_usage': 0,
                'max_file_size': self.default_max_file_size,
                'reset_date': self._calculate_next_reset_date()
            }
        )
        
        # Reset automatique si nouveau mois
        if timezone.now() >= quota.reset_date:
            self._reset_quota(quota)
        
        return quota
    
    def check_quota(self, brand, file_size):
        """Vérifie si une conversion est autorisée"""
        quota = self.get_or_create_quota(brand)
        return quota.can_convert(file_size)
    
    def increment_usage(self, brand):
        """Incrémente l'usage du quota"""
        quota = self.get_or_create_quota(brand)
        quota.increment_usage()
    
    def _reset_quota(self, quota):
        """Reset le quota pour le nouveau mois"""
        quota.current_month_usage = 0
        quota.reset_date = self._calculate_next_reset_date()
        quota.save(update_fields=['current_month_usage', 'reset_date'])
        
        logger.info(f"Quota reset pour brand {quota.brand.id}")
    
    def _calculate_next_reset_date(self):
        """Calcule la prochaine date de reset (1er du mois suivant)"""
        now = timezone.now()
        if now.month == 12:
            return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)