# backend/file_converter/tasks.py

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .services.conversion_service import ConversionService
from .models import FileConversion

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2)
def convert_file_task(self, conversion_id: int):
    """Tâche de conversion de fichier"""
    
    try:
        logger.info(f"Début conversion {conversion_id}")
        
        service = ConversionService()
        success = service.perform_conversion(conversion_id)
        
        if success:
            logger.info(f"Conversion {conversion_id} réussie")
            return {"status": "success", "conversion_id": conversion_id}
        else:
            logger.error(f"Conversion {conversion_id} échouée")
            return {"status": "failed", "conversion_id": conversion_id}
            
    except Exception as exc:
        logger.error(f"Erreur conversion {conversion_id}: {str(exc)}")
        
        # Retry avec délai exponentiel
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries  # 2, 4 secondes
            logger.info(f"Retry conversion {conversion_id} dans {countdown}s")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Marquer comme échec après max retries
        try:
            conversion = FileConversion.objects.get(id=conversion_id)
            conversion.status = 'failed'
            conversion.error_message = f"Échec après {self.max_retries} tentatives: {str(exc)}"
            conversion.save()
        except FileConversion.DoesNotExist:
            pass
        
        return {"status": "failed", "conversion_id": conversion_id, "error": str(exc)}

@shared_task
def cleanup_expired_conversions():
    """Nettoie les conversions expirées"""
    try:
        service = ConversionService()
        result = service.cleanup_expired_files()
        logger.info(f"Nettoyage terminé: {result}")
        return result
    except Exception as e:
        logger.error(f"Erreur nettoyage: {str(e)}")
        return {"error": str(e)}

@shared_task
def reset_monthly_quotas():
    """Remet à zéro les quotas mensuels"""
    try:
        from .models import ConversionQuota
        
        quotas_to_reset = ConversionQuota.objects.filter(
            reset_date__lt=timezone.now()
        )
        
        count = 0
        for quota in quotas_to_reset:
            quota.current_month_usage = 0
            quota.reset_date = timezone.now().replace(day=1) + timedelta(days=32)
            quota.save()
            count += 1
        
        logger.info(f"{count} quotas mensuels remis à zéro")
        return {"reset": count}
        
    except Exception as e:
        logger.error(f"Erreur reset quotas: {str(e)}")
        return {"error": str(e)}