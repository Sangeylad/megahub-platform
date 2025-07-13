# backend/ai_core/services/job_service.py

import uuid
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.db import transaction

from ..models import AIJob, AIJobType, AIJobStatus

logger = logging.getLogger(__name__)

class JobService:
    """Service central gestion jobs IA"""
    
    @staticmethod
    @transaction.atomic
    def create_ai_job(
        job_type_name: str,
        brand,
        created_by,
        description: str = "",
        input_data: Dict[str, Any] = None,
        priority: str = 'normal'
    ) -> AIJob:
        """Créer un nouveau job IA"""
        try:
            job_type = AIJobType.objects.get(name=job_type_name)
        except AIJobType.DoesNotExist:
            raise ValueError(f"Job type '{job_type_name}' non trouvé")
        
        job_id = f"ai_{uuid.uuid4().hex[:12]}"
        
        # Déterminer si async selon durée estimée
        is_async = job_type.estimated_duration_seconds > 5
        
        ai_job = AIJob.objects.create(
            job_id=job_id,
            job_type=job_type,
            brand=brand,
            created_by=created_by,
            description=description,
            input_data=input_data or {},
            priority=priority,
            is_async=is_async
        )
        
        logger.info(f"Job IA créé: {job_id} ({job_type_name}) - async: {is_async}")
        return ai_job
    
    @staticmethod
    def start_job(ai_job: AIJob, task_id: str = None) -> AIJob:
        """Marquer job comme démarré"""
        ai_job.status = AIJobStatus.RUNNING
        ai_job.started_at = timezone.now()
        if task_id:
            ai_job.task_id = task_id
        ai_job.save(update_fields=['status', 'started_at', 'task_id'])
        
        logger.info(f"Job IA démarré: {ai_job.job_id}")
        return ai_job
    
    @staticmethod
    def complete_job(
        ai_job: AIJob, 
        result_data: Dict[str, Any], 
        progress: int = 100
    ) -> AIJob:
        """Marquer job comme terminé avec succès"""
        ai_job.status = AIJobStatus.COMPLETED
        ai_job.completed_at = timezone.now()
        ai_job.result_data = result_data
        ai_job.progress_percentage = progress
        ai_job.save(update_fields=[
            'status', 'completed_at', 'result_data', 'progress_percentage'
        ])
        
        logger.info(f"Job IA terminé: {ai_job.job_id}")
        return ai_job
    
    @staticmethod
    def fail_job(ai_job: AIJob, error_message: str) -> AIJob:
        """Marquer job comme échoué"""
        ai_job.status = AIJobStatus.FAILED
        ai_job.completed_at = timezone.now()
        ai_job.error_message = error_message
        ai_job.save(update_fields=['status', 'completed_at', 'error_message'])
        
        logger.error(f"Job IA échoué: {ai_job.job_id} - {error_message}")
        return ai_job
    
    @staticmethod
    def update_progress(ai_job: AIJob, progress: int) -> AIJob:
        """Mettre à jour progression"""
        ai_job.progress_percentage = min(max(progress, 0), 100)
        ai_job.save(update_fields=['progress_percentage'])
        return ai_job
