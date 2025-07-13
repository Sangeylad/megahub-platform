# backend/task_persistence/services/persistence_service.py

from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
from task_core.models import BaseTask
from task_core.services import TaskExecutor
from ..models import PersistentJob, JobCheckpoint, JobState

class PersistenceService:
    """Service pour la gestion de la persistance des jobs"""
    
    @staticmethod
    @transaction.atomic
    def create_persistent_job(
        task_type: str,
        brand_id: int,
        created_by_id: int,
        job_data: Dict[str, Any],
        total_steps: int = 1,
        description: str = '',
        priority: str = 'normal'
    ) -> PersistentJob:
        """Crée un job persistant complet"""
        
        # Créer la BaseTask
        base_task = TaskExecutor.create_task(
            task_type=task_type,
            brand_id=brand_id,
            created_by_id=created_by_id,
            context_data={'persistent': True},
            priority=priority,
            description=description
        )
        
        # Créer le PersistentJob
        persistent_job = PersistentJob.objects.create(
            base_task=base_task,
            job_data=job_data,
            total_steps=total_steps,
            can_resume=True
        )
        
        # Créer le JobState
        JobState.objects.create(
            persistent_job=persistent_job,
            max_retries=3
        )
        
        return persistent_job
    
    @staticmethod
    def save_checkpoint(
        persistent_job: PersistentJob,
        step_name: str,
        checkpoint_data: Dict[str, Any]
    ) -> JobCheckpoint:
        """Sauvegarde un point de contrôle"""
        
        return JobCheckpoint.objects.create(
            persistent_job=persistent_job,
            step_name=step_name,
            checkpoint_data=checkpoint_data,
            is_recovery_point=True
        )
    
    @staticmethod
    def update_progress(
        persistent_job: PersistentJob,
        completed_steps: int,
        current_step: str,
        estimated_remaining_minutes: Optional[int] = None
    ):
        """Met à jour le progrès du job"""
        
        progress = (completed_steps / persistent_job.total_steps) * 100
        
        update_fields = [
            'completed_steps', 'current_step', 'progress_percentage'
        ]
        
        persistent_job.completed_steps = completed_steps
        persistent_job.current_step = current_step
        persistent_job.progress_percentage = progress
        
        if estimated_remaining_minutes is not None:
            persistent_job.estimated_remaining_minutes = estimated_remaining_minutes
            update_fields.append('estimated_remaining_minutes')
        
        persistent_job.save(update_fields=update_fields)
    
    @staticmethod
    def mark_job_failed(
        persistent_job: PersistentJob,
        error_message: str,
        page_id: Optional[int] = None
    ):
        """Marque un job comme échoué avec log d'erreur"""
        
        # Mettre à jour BaseTask
        persistent_job.base_task.status = 'failed'
        persistent_job.base_task.save(update_fields=['status'])
        
        # Ajouter l'erreur au JobState
        job_state = persistent_job.job_state
        job_state.add_error(error_message, page_id)
        job_state.retry_count += 1
        job_state.save(update_fields=['retry_count'])
