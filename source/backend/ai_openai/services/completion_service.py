# backend/ai_openai/services/completion_service.py

import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone
from ai_core.services import JobService
from ai_core.models import AIJob, AIJobStatus
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)

class CompletionService:
    """Service pour orchestration des completions OpenAI"""
    
    @staticmethod
    def create_completion_job(
        job_type_name: str,
        messages: List[Dict],
        company,
        brand,
        user,
        model: str = "gpt-4o",
        description: str = "",
        **completion_kwargs
    ) -> AIJob:
        """Crée un job de completion complet"""
        
        try:
            # 1. Créer le job IA core
            ai_job = JobService.create_job(
                job_type_name=job_type_name,
                brand=brand,
                created_by=user,
                description=description,
                context_data={
                    'model': model,
                    'messages_count': len(messages)
                }
            )
            
            # 2. Créer le service OpenAI
            openai_service = OpenAIService(company)
            
            # 3. Créer l'extension completion
            completion = openai_service.create_completion(
                ai_job=ai_job,
                messages=messages,
                model=model,
                **completion_kwargs
            )
            
            logger.info(f"Job completion créé: {ai_job.job_id}")
            return ai_job
            
        except Exception as e:
            logger.error(f"Erreur création job completion: {str(e)}")
            raise
    
    @staticmethod
    def execute_completion_job(job_id: str) -> Dict[str, Any]:
        """Exécute un job de completion (appelé par task_core)"""
        
        try:
            # 1. Récupérer le job
            ai_job = AIJob.objects.get(job_id=job_id)
            completion = ai_job.openai_completion
            
            # 2. Marquer comme démarré
            JobService.start_job(job_id)
            
            # 3. Créer le service OpenAI
            openai_service = OpenAIService(ai_job.brand.company)
            
            # 4. Exécuter la completion
            response = openai_service.execute_completion_sync(completion)
            
            # 5. Marquer comme terminé
            JobService.complete_job(
                job_id=job_id,
                result_data={
                    'completion_text': completion.completion_text,
                    'tokens_used': completion.openai_usage.total_tokens,
                    'cost_usd': float(completion.openai_usage.cost_usd)
                }
            )
            
            logger.info(f"Job completion exécuté avec succès: {job_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erreur exécution job completion {job_id}: {str(e)}")
            JobService.fail_job(job_id, str(e))
            raise
    
    @staticmethod
    def get_completion_result(job_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le résultat d'une completion"""
        try:
            ai_job = AIJob.objects.get(job_id=job_id)
            
            if ai_job.status != AIJobStatus.COMPLETED:
                return None
            
            completion = ai_job.openai_completion
            usage = ai_job.openai_usage
            
            return {
                'job_id': job_id,
                'status': ai_job.status,
                'completion_text': completion.completion_text,
                'model': completion.model,
                'tokens_used': usage.total_tokens,
                'cost_usd': float(usage.cost_usd),
                'execution_time_ms': usage.execution_time_ms,
                'completed_at': ai_job.completed_at
            }
            
        except AIJob.DoesNotExist:
            logger.error(f"Job introuvable: {job_id}")
            return None
