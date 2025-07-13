# backend/file_compressor/tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .services.file_optimization_service import FileOptimizationService
from .models import FileOptimization, OptimizationQuota

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2)
def optimize_file_task(self, optimization_id: str):
    """Tâche d'optimisation de fichiers avec retry"""
    try:
        logger.info(f"Début optimisation {optimization_id}")
        
        service = FileOptimizationService()
        success = service.perform_optimization(optimization_id)
        
        if success:
            logger.info(f"Optimisation {optimization_id} réussie")
            return {"status": "success", "optimization_id": optimization_id}
        else:
            logger.error(f"Optimisation {optimization_id} échouée")
            return {"status": "failed", "optimization_id": optimization_id}
            
    except Exception as exc:
        logger.error(f"Erreur optimisation {optimization_id}: {str(exc)}")
        
        # Retry avec délai croissant
        if self.request.retries < self.max_retries:
            countdown = 60 * (self.request.retries + 1)  # 60, 120 secondes
            logger.info(f"Retry optimisation {optimization_id} dans {countdown}s")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Marquer comme échec après retries
        try:
            optimization = FileOptimization.objects.get(id=optimization_id)
            optimization.status = 'failed'
            optimization.error_message = f"Échec après {self.max_retries} tentatives: {str(exc)}"
            optimization.save()
        except FileOptimization.DoesNotExist:
            pass
            
        return {"status": "failed", "optimization_id": optimization_id, "error": str(exc)}

@shared_task
def cleanup_expired_optimizations():
    """Nettoyage des optimisations expirées"""
    try:
        service = FileOptimizationService()
        
        # Optimisations expirées
        expired_optimizations = FileOptimization.objects.filter(
            expires_at__lt=timezone.now(),
            status='completed'
        )
        
        deleted_files = 0
        deleted_storage_paths = []
        
        for optimization in expired_optimizations:
            # Suppression des fichiers de storage
            if optimization.download_url:
                try:
                    # Extraction du chemin de storage depuis l'URL
                    storage_path = f"optimizations/{optimization.brand.id}/{optimization.id}/{optimization.optimized_filename}"
                    
                    from django.core.files.storage import default_storage
                    if default_storage.exists(storage_path):
                        default_storage.delete(storage_path)
                        deleted_files += 1
                        deleted_storage_paths.append(storage_path)
                        
                    # Suppression du dossier d'upload aussi
                    upload_path = f"uploads/optimizations/{optimization.id}"
                    if default_storage.exists(upload_path):
                        # Supprimer tous les fichiers dans le dossier
                        import os
                        from django.conf import settings
                        full_upload_path = os.path.join(settings.MEDIA_ROOT, upload_path)
                        if os.path.exists(full_upload_path):
                            import shutil
                            shutil.rmtree(full_upload_path)
                            
                except Exception as e:
                    logger.warning(f"Erreur suppression fichier {optimization.id}: {str(e)}")
        
        # Suppression des enregistrements
        deleted_count = expired_optimizations.delete()[0]
        
        result = {
            'deleted_optimizations': deleted_count,
            'deleted_files': deleted_files,
            'deleted_paths': deleted_storage_paths,
            'status': 'success'
        }
        
        logger.info(f"Nettoyage optimisations: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erreur nettoyage optimisations: {str(e)}")
        return {"error": str(e)}

@shared_task
def reset_monthly_quotas():
    """Reset des quotas mensuels d'optimisation"""
    try:
        now = timezone.now()
        quotas_to_reset = OptimizationQuota.objects.filter(
            reset_date__lt=now
        )
        
        updated_count = 0
        for quota in quotas_to_reset:
            quota.current_month_usage = 0
            # Prochain reset : premier du mois suivant
            next_month = now.replace(day=1) + timedelta(days=32)
            quota.reset_date = next_month.replace(day=1)
            quota.save()
            updated_count += 1
        
        logger.info(f"Quotas mensuels reset: {updated_count}")
        return {"reset": updated_count}
        
    except Exception as e:
        logger.error(f"Erreur reset quotas: {str(e)}")
        return {"error": str(e)}

@shared_task
def generate_optimization_stats():
    """Génération des statistiques d'optimisation (tâche périodique)"""
    try:
        from django.db import models
        from brands_core.models import Brand
        
        # Stats globales par brand
        stats_by_brand = {}
        
        for brand in Brand.objects.all():
            optimizations = FileOptimization.objects.filter(brand=brand)
            successful = optimizations.filter(status='completed')
            
            if successful.exists():
                total_original_size = successful.aggregate(
                    total=models.Sum('original_size')
                )['total'] or 0
                
                total_optimized_size = successful.aggregate(
                    total=models.Sum('optimized_size')
                )['total'] or 0
                
                total_saved = total_original_size - total_optimized_size
                avg_reduction = (total_saved / total_original_size * 100) if total_original_size > 0 else 0
                
                stats_by_brand[brand.id] = {
                    'brand_name': brand.name,
                    'total_optimizations': optimizations.count(),
                    'successful_optimizations': successful.count(),
                    'total_space_saved_mb': total_saved / (1024 * 1024),
                    'average_reduction_percentage': avg_reduction,
                    'last_optimization': optimizations.order_by('-created_at').first().created_at if optimizations.exists() else None
                }
        
        logger.info(f"Stats générées pour {len(stats_by_brand)} brands")
        return {"stats_generated": len(stats_by_brand), "brands": list(stats_by_brand.keys())}
        
    except Exception as e:
        logger.error(f"Erreur génération stats: {str(e)}")
        return {"error": str(e)}