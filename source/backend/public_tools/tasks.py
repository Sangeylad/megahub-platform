# backend/public_tools/tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .services.public_conversion_service import PublicConversionService
from .models import PublicFileConversion, PublicConversionQuota

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=1)
def convert_public_file_task(self, conversion_id: str):
    """Tâche de conversion publique avec retry limité"""
    try:
        logger.info(f"Début conversion publique {conversion_id}")
        
        service = PublicConversionService()
        success = service.perform_public_conversion(conversion_id)
        
        if success:
            logger.info(f"Conversion publique {conversion_id} réussie")
            return {"status": "success", "conversion_id": conversion_id}
        else:
            logger.error(f"Conversion publique {conversion_id} échouée")
            return {"status": "failed", "conversion_id": conversion_id}
    
    except Exception as exc:
        logger.error(f"Erreur conversion publique {conversion_id}: {str(exc)}")
        
        # Un seul retry avec délai de 30 secondes
        if self.request.retries < self.max_retries:
            logger.info(f"Retry conversion publique {conversion_id} dans 30s")
            raise self.retry(countdown=30, exc=exc)
        
        # Marquer comme échec après retry
        try:
            conversion = PublicFileConversion.objects.get(id=conversion_id)
            conversion.status = 'failed'
            conversion.error_message = f"Échec après retry: {str(exc)}"
            conversion.save()
        except PublicFileConversion.DoesNotExist:
            pass
        
        return {"status": "failed", "conversion_id": conversion_id, "error": str(exc)}

@shared_task
def cleanup_public_conversions():
    """Nettoyage agressif des conversions publiques expirées"""
    try:
        service = PublicConversionService()
        result = service.cleanup_expired_files()
        
        logger.info(f"Nettoyage public terminé: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur nettoyage public: {str(e)}")
        return {"error": str(e)}

@shared_task
def cleanup_old_quotas():
    """Nettoie les quotas anciens (7 jours)"""
    try:
        old_date = timezone.now() - timedelta(days=7)
        deleted_count = PublicConversionQuota.objects.filter(
            last_conversion__lt=old_date
        ).delete()[0]
        
        logger.info(f"Quotas anciens supprimés: {deleted_count}")
        return {"deleted": deleted_count}
        
    except Exception as e:
        logger.error(f"Erreur nettoyage quotas: {str(e)}")
        return {"error": str(e)}

@shared_task
def reset_hourly_quotas():
    """Reset les quotas horaires"""
    try:
        updated_count = PublicConversionQuota.objects.filter(
            hourly_usage__gt=0
        ).update(hourly_usage=0)
        
        logger.info(f"Quotas horaires reset: {updated_count}")
        return {"reset": updated_count}
        
    except Exception as e:
        logger.error(f"Erreur reset quotas: {str(e)}")
        return {"error": str(e)}
    
# Ajouter à la fin du fichier existant

@shared_task(bind=True, max_retries=1)
def compress_public_files_task(self, compression_id: str):
    """Tâche de compression publique avec retry limité"""
    try:
        logger.info(f"Début compression publique {compression_id}")
        
        from .services.public_compression_service import PublicCompressionService
        service = PublicCompressionService()
        success = service.perform_public_compression(compression_id)
        
        if success:
            logger.info(f"Compression publique {compression_id} réussie")
            return {"status": "success", "compression_id": compression_id}
        else:
            logger.error(f"Compression publique {compression_id} échouée")
            return {"status": "failed", "compression_id": compression_id}
            
    except Exception as exc:
        logger.error(f"Erreur compression publique {compression_id}: {str(exc)}")
        
        # Un seul retry avec délai de 30 secondes
        if self.request.retries < self.max_retries:
            logger.info(f"Retry compression publique {compression_id} dans 30s")
            raise self.retry(countdown=30, exc=exc)
        
        # Marquer comme échec après retry
        try:
            from .models import PublicFileCompression
            compression = PublicFileCompression.objects.get(id=compression_id)
            compression.status = 'failed'
            compression.error_message = f"Échec après retry: {str(exc)}"
            compression.save()
        except:
            pass
            
        return {"status": "failed", "compression_id": compression_id, "error": str(exc)}

@shared_task
def cleanup_public_compressions():
    """Nettoyage agressif des compressions publiques expirées"""
    try:
        from .services.public_compression_service import PublicCompressionService
        service = PublicCompressionService()
        result = service.cleanup_expired_files()
        
        logger.info(f"Nettoyage compressions publiques: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur nettoyage compressions publiques: {str(e)}")
        return {"error": str(e)}
    
    
# Ajouter à la fin du fichier existant

@shared_task(bind=True, max_retries=1)
def optimize_public_file_task(self, optimization_id: str):
    """Tâche d'optimisation publique avec retry limité"""
    try:
        logger.info(f"Début optimisation publique {optimization_id}")
        
        from .services.public_optimization_service import PublicOptimizationService
        service = PublicOptimizationService()
        success = service.perform_public_optimization(optimization_id)
        
        if success:
            logger.info(f"Optimisation publique {optimization_id} réussie")
            return {"status": "success", "optimization_id": optimization_id}
        else:
            logger.error(f"Optimisation publique {optimization_id} échouée")
            return {"status": "failed", "optimization_id": optimization_id}
            
    except Exception as exc:
        logger.error(f"Erreur optimisation publique {optimization_id}: {str(exc)}")
        
        # Un seul retry avec délai de 30 secondes
        if self.request.retries < self.max_retries:
            logger.info(f"Retry optimisation publique {optimization_id} dans 30s")
            raise self.retry(countdown=30, exc=exc)
        
        # Marquer comme échec après retry
        try:
            from .models import PublicFileOptimization
            optimization = PublicFileOptimization.objects.get(id=optimization_id)
            optimization.status = 'failed'
            optimization.error_message = f"Échec après retry: {str(exc)}"
            optimization.save()
        except:
            pass
            
        return {"status": "failed", "optimization_id": optimization_id, "error": str(exc)}

@shared_task
def cleanup_public_optimizations():
    """Nettoyage agressif des optimisations publiques expirées"""
    try:
        from .services.public_optimization_service import PublicOptimizationService
        service = PublicOptimizationService()
        result = service.cleanup_expired_files()
        
        logger.info(f"Nettoyage optimisations publiques: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur nettoyage optimisations publiques: {str(e)}")
        return {"error": str(e)}

@shared_task
def reset_hourly_public_quotas():
    """Reset des quotas horaires publics"""
    try:
        from .models import PublicOptimizationQuota
        
        updated_count = PublicOptimizationQuota.objects.filter(
            hourly_usage__gt=0
        ).update(hourly_usage=0)
        
        logger.info(f"Quotas horaires publics reset: {updated_count}")
        return {"reset": updated_count}
        
    except Exception as e:
        logger.error(f"Erreur reset quotas publics: {str(e)}")
        return {"error": str(e)}