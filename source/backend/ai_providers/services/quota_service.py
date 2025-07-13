# backend/ai_providers/services/quota_service.py

import logging
from decimal import Decimal
from django.utils import timezone
from datetime import date
from typing import Dict, Any

from ..models import AIQuota, AIProvider

logger = logging.getLogger(__name__)

class QuotaService:
    """Service gestion quotas IA"""
    
    @staticmethod
    def get_quota_status(company, provider_name: str) -> Dict[str, Any]:
        """Status quota pour company/provider"""
        try:
            provider = AIProvider.objects.get(name=provider_name)
            quota = AIQuota.objects.get(company=company, provider=provider)
        except (AIProvider.DoesNotExist, AIQuota.DoesNotExist):
            return {
                'has_quota': False,
                'tokens_remaining': 0,
                'cost_remaining': 0,
                'is_over_limit': True
            }
        
        # Reset mensuel si nécessaire
        QuotaService._reset_if_needed(quota)
        
        tokens_remaining = quota.monthly_token_limit - quota.current_tokens_used
        cost_remaining = quota.monthly_cost_limit - quota.current_cost_used
        
        return {
            'has_quota': True,
            'tokens_used': quota.current_tokens_used,
            'tokens_remaining': max(0, tokens_remaining),
            'cost_used': float(quota.current_cost_used),
            'cost_remaining': float(max(0, cost_remaining)),
            'is_over_limit': tokens_remaining <= 0 or cost_remaining <= 0,
            'reset_date': quota.last_reset_date
        }
    
    @staticmethod
    def consume_quota(
        company, 
        provider_name: str, 
        tokens_used: int, 
        cost: Decimal
    ) -> bool:
        """Consommer quota et vérifier limites"""
        try:
            provider = AIProvider.objects.get(name=provider_name)
            quota, created = AIQuota.objects.get_or_create(
                company=company, 
                provider=provider
            )
        except AIProvider.DoesNotExist:
            logger.error(f"Provider non trouvé: {provider_name}")
            return False
        
        # Reset si nécessaire
        QuotaService._reset_if_needed(quota)
        
        # Vérifier limites avant consommation
        new_tokens = quota.current_tokens_used + tokens_used
        new_cost = quota.current_cost_used + cost
        
        if (new_tokens > quota.monthly_token_limit or 
            new_cost > quota.monthly_cost_limit):
            logger.warning(
                f"Quota dépassé pour {company.name}: "
                f"tokens {new_tokens}/{quota.monthly_token_limit}, "
                f"coût {new_cost}/{quota.monthly_cost_limit}"
            )
            return False
        
        # Consommer
        quota.current_tokens_used = new_tokens
        quota.current_cost_used = new_cost
        quota.save(update_fields=['current_tokens_used', 'current_cost_used'])
        
        return True
    
    @staticmethod
    def _reset_if_needed(quota: AIQuota) -> None:
        """Reset quota si nouveau mois"""
        today = date.today()
        if quota.last_reset_date.month != today.month:
            quota.current_tokens_used = 0
            quota.current_cost_used = Decimal('0.00')
            quota.last_reset_date = today
            quota.save(update_fields=[
                'current_tokens_used', 'current_cost_used', 'last_reset_date'
            ])
            logger.info(f"Quota reset pour {quota.company.name}")
