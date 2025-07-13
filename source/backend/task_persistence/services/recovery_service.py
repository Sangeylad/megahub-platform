# backend/task_persistence/services/recovery_service.py

from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
from ..models import PersistentJob, JobCheckpoint
from .persistence_service import PersistenceService

class RecoveryService:
    """Service pour la reprise de jobs interrompus"""
    
    @staticmethod
    def find_resumable_jobs(brand_id: Optional[int] = None) -> List[PersistentJob]:
        """Trouve tous les jobs qui peuvent être repris"""
        
        queryset = PersistentJob.objects.filter(
            can_resume=True,
            base_task__status__in=['failed', 'cancelled'],
            completed_steps__gt=0
        ).select_related('base_task', 'job_state')
        
        if brand_id:
            queryset = queryset.filter(base_task__brand_id=brand_id)
        
        return list(queryset)
    
    @staticmethod
    @transaction.atomic
    def resume_job(persistent_job: PersistentJob) -> Dict[str, Any]:
        """Reprend un job depuis son dernier checkpoint"""
        
        if not persistent_job.is_resumable():
            return {
                'success': False,
                'error': 'Job cannot be resumed'
            }
        
        # Vérifier les retries
        job_state = persistent_job.job_state
        if not job_state.can_retry():
            return {
                'success': False,
                'error': f'Max retries ({job_state.max_retries}) exceeded'
            }
        
        # Récupérer le dernier checkpoint
        latest_checkpoint = persistent_job.get_latest_checkpoint()
        if not latest_checkpoint:
            return {
                'success': False,
                'error': 'No checkpoint found for recovery'
            }
        
        # Préparer les données de reprise
        recovery_data = {
            'checkpoint_data': latest_checkpoint.checkpoint_data,
            'resume_from_step': latest_checkpoint.step_name,
            'completed_steps': persistent_job.completed_steps,
            'job_data': persistent_job.job_data
        }
        
        # Mettre à jour l'état
        persistent_job.resume_from_step = latest_checkpoint.step_name
        persistent_job.base_task.status = 'pending'
        persistent_job.base_task.save(update_fields=['status'])
        persistent_job.save(update_fields=['resume_from_step'])
        
        return {
            'success': True,
            'recovery_data': recovery_data,
            'message': f'Job resumed from step: {latest_checkpoint.step_name}'
        }
    
    @staticmethod
    def cleanup_old_checkpoints(days_old: int = 30):
        """Nettoie les anciens checkpoints"""
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        # Supprimer les checkpoints des jobs terminés
        deleted_count = JobCheckpoint.objects.filter(
            created_at__lt=cutoff_date,
            persistent_job__base_task__status__in=['completed', 'cancelled']
        ).delete()[0]
        
        return {
            'deleted_checkpoints': deleted_count,
            'cutoff_date': cutoff_date
        }
