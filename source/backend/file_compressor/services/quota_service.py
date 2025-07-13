# backend/file_compressor/services/quota_service.py
from typing import Tuple
from django.utils import timezone
from datetime import timedelta
import logging

from ..models import CompressionQuota

logger = logging.getLogger(__name__)

class QuotaService:
    """Service de gestion des quotas de compression"""
    
    @staticmethod
    def check_brand_quota(brand, files_count: int = 0, total_size: int = 0) -> Tuple[bool, str]:
        """Vérifie si une brand peut effectuer une compression"""
        try:
            quota, created = CompressionQuota.objects.get_or_create(
                brand=brand,
                defaults={
                    'reset_date': timezone.now() + timedelta(days=30)
                }
            )
            
            # Reset mensuel automatique
            if timezone.now() > quota.reset_date:
                quota.current_month_usage = 0
                quota.reset_date = timezone.now() + timedelta(days=30)
                quota.save()
            
            return quota.can_compress(files_count, total_size)
            
        except Exception as e:
            logger.error(f"Erreur vérification quota: {str(e)}")
            return False, "Erreur de vérification des quotas"
    
    @staticmethod
    def increment_brand_usage(brand):
        """Incrémente l'usage d'une brand"""
        try:
            quota = CompressionQuota.objects.get(brand=brand)
            quota.increment_usage()
        except CompressionQuota.DoesNotExist:
            logger.warning(f"Quota non trouvé pour brand {brand.id}")