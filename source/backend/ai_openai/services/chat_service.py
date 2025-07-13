# backend/ai_openai/services/chat_service.py

import logging
from typing import Dict, List, Optional, Any
from django.db import transaction

from ai_core.services import JobService
from ai_providers.services import QuotaService
from ..models import OpenAIJob
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)

class ChatService:
    """Service chat completions avec support multi-modèles"""
    
    @staticmethod
    @transaction.atomic
    def create_chat_job(
        messages: List[Dict],
        brand,
        created_by,
        model: str = 'gpt-4o',
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,  # 🆕 Paramètre O3
        description: str = "",
        tools: Optional[List] = None,
        tool_resources: Optional[Dict] = None,
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Créer job chat completion avec auto-détection modèle"""
        
        # 🎯 AUTO-CONFIGURATION SELON MODÈLE
        is_new_gen = model.startswith('o3') or model in ['gpt-4.1']
        
        # Paramètres par défaut selon génération
        if is_new_gen:
            if model.startswith('o3'):
                # O3 configuration
                default_reasoning = reasoning_effort or 'medium'
                default_temp = None  # O3 n'utilise pas temperature
                default_max_tokens = max_completion_tokens or max_tokens or 1000
            else:
                # gpt-4.1 configuration
                default_reasoning = None
                default_temp = temperature or 1.0
                default_max_tokens = max_tokens or 10000
        else:
            # Legacy configuration
            default_reasoning = None
            default_temp = temperature or 0.7
            default_max_tokens = max_tokens or 1000
        
        # 1. Créer AIJob central
        ai_job = JobService.create_ai_job(
            job_type_name='chat_completion',
            brand=brand,
            created_by=created_by,
            description=description or f"Chat {model}",
            input_data={
                'model': model,
                'messages_count': len(messages),
                'has_tools': bool(tools),
                'is_new_generation': is_new_gen,
                'reasoning_effort': default_reasoning if model.startswith('o3') else None
            }
        )
        
        # 2. Extension OpenAI avec paramètres adaptés
        openai_job = OpenAIJob.objects.create(
            ai_job=ai_job,
            model=model,
            temperature=default_temp,  # 🔧 None pour O3
            max_tokens=default_max_tokens if not is_new_gen else None,  # Legacy seulement
            reasoning_effort=default_reasoning,
            max_completion_tokens=default_max_tokens if is_new_gen else None,  # O3/GPT-4.1 seulement
            messages=messages,
            messages_format='structured' if is_new_gen else 'legacy',
            tools=tools or [],
            tool_resources=tool_resources or {},
            response_format=response_format or {}
        )
        
        # 3. Décision sync/async (inchangé)
        if ai_job.is_async:
            from ..tasks import execute_chat_completion_task
            task = execute_chat_completion_task.delay(ai_job.id)
            
            JobService.start_job(ai_job, task_id=task.id)
            
            return {
                'job_id': ai_job.job_id,
                'status': 'async',
                'task_id': task.id,
                'message': f'Job started asynchronously with {model}'
            }
        else:
            try:
                result = ChatService._execute_chat(openai_job)
                JobService.complete_job(ai_job, result)
                
                return {
                    'job_id': ai_job.job_id,
                    'status': 'completed',
                    'result': result
                }
            except Exception as e:
                JobService.fail_job(ai_job, str(e))
                raise
    
    @staticmethod
    def _execute_chat(openai_job: OpenAIJob) -> Dict[str, Any]:
        """Exécuter chat completion avec paramètres adaptés"""
        ai_job = openai_job.ai_job
        
        # Service OpenAI
        openai_service = OpenAIService(company=ai_job.brand.company)
        
        # Vérifier quota
        quota_status = QuotaService.get_quota_status(
            ai_job.brand.company, 'openai'
        )
        if quota_status.get('is_over_limit'):
            raise Exception("Quota OpenAI dépassé")
        
        # 🎯 PARAMÈTRES SELON MODÈLE
        call_params = {
            'messages': openai_job.messages,
            'model': openai_job.model
        }
        
        # Ajout paramètres conditionnels selon modèle
        if openai_job.temperature is not None:
            call_params['temperature'] = openai_job.temperature
        
        # 🔧 DISTINCTION max_tokens vs max_completion_tokens
        if openai_job.is_new_generation_model:
            # O3/GPT-4.1 utilisent max_completion_tokens
            if openai_job.max_completion_tokens:
                call_params['max_completion_tokens'] = openai_job.max_completion_tokens
        else:
            # Legacy utilisent max_tokens
            if openai_job.max_tokens:
                call_params['max_tokens'] = openai_job.max_tokens
        
        if openai_job.reasoning_effort:
            call_params['reasoning_effort'] = openai_job.reasoning_effort
        
        if openai_job.tools:
            call_params['tools'] = openai_job.tools
        
        if openai_job.tool_resources:
            call_params['tool_resources'] = openai_job.tool_resources
        
        if openai_job.response_format:
            call_params['response_format'] = openai_job.response_format
        
        # 🆕 Log des paramètres pour debug
        logger.info(f"Chat completion {openai_job.model} with params: {list(call_params.keys())}")
        
        # Appel OpenAI avec paramètres adaptés
        response = openai_service.chat_completion(**call_params)
        
        # Extraire métriques
        usage = response.get('usage', {})
        openai_job.prompt_tokens = usage.get('prompt_tokens', 0)
        openai_job.completion_tokens = usage.get('completion_tokens', 0)
        openai_job.total_tokens = usage.get('total_tokens', 0)
        openai_job.openai_id = response.get('id', '')
        openai_job.save()
        
        # 🆕 Calcul coût selon modèle
        cost_per_token = ChatService._get_cost_per_token(openai_job.model)
        total_cost = openai_job.total_tokens * cost_per_token
        
        # Consommer quota
        QuotaService.consume_quota(
            ai_job.brand.company,
            'openai',
            openai_job.total_tokens,
            total_cost
        )
        
        return {
            'response': response,
            'tokens_used': openai_job.total_tokens,
            'cost_usd': total_cost,
            'model': openai_job.model,
            'generation': 'new' if openai_job.is_new_generation_model else 'legacy'
        }
    
    @staticmethod
    def _get_cost_per_token(model: str) -> float:
        """Calcul coût par token selon modèle"""
        # 🆕 Coûts approximatifs selon modèles OpenAI
        costs = {
            'gpt-4o': 0.000002,           # $2/1M tokens
            'gpt-4-turbo': 0.000003,      # $3/1M tokens
            'gpt-3.5-turbo': 0.000001,    # $1/1M tokens
            'o3': 0.000020,               # $20/1M tokens (estimation élevée)
            'o3-mini': 0.000005,          # $5/1M tokens (estimation)
            'gpt-4.1': 0.000004,          # $4/1M tokens (estimation)
        }
        return costs.get(model, 0.000002)  # Défaut GPT-4o