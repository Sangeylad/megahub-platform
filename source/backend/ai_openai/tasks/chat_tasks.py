# backend/ai_openai/tasks/chat_tasks.py

import logging
from celery import shared_task
from django.db import transaction

from ai_core.models import AIJob
from ai_core.services import JobService
from ..services import ChatService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def execute_chat_completion_task(self, ai_job_id: int):
    """Exécuter chat completion en async via task_core"""
    try:
        with transaction.atomic():
            ai_job = AIJob.objects.select_related('openai_job').get(id=ai_job_id)
            openai_job = ai_job.openai_job
            
            # Marquer comme running
            JobService.start_job(ai_job, task_id=self.request.id)
            
            # Exécuter
            result = ChatService._execute_chat(openai_job)
            
            # Compléter
            JobService.complete_job(ai_job, result)
            
            logger.info(f"Chat completion réussi: {ai_job.job_id}")
            return result
            
    except Exception as e:
        logger.error(f"Chat completion échoué: {str(e)}", exc_info=True)
        
        # Marquer comme failed
        try:
            ai_job = AIJob.objects.get(id=ai_job_id)
            JobService.fail_job(ai_job, str(e))
        except:
            pass
        
        # Retry si possible
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        raise e
