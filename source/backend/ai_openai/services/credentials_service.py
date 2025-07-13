# backend/ai_openai/services/credentials_service.py

import logging
from typing import Optional
from django.core.exceptions import ValidationError
from ..models import OpenAICredentials, OpenAIProvider
from company_core.models import Company

logger = logging.getLogger(__name__)

class CredentialsService:
    """Service pour gestion des credentials OpenAI"""
    
    @staticmethod
    def get_credentials_for_company(company: Company) -> Optional[OpenAICredentials]:
        """Récupère les credentials pour une company"""
        try:
            return OpenAICredentials.objects.get(
                company=company,
                is_active=True,
                validation_status='valid'
            )
        except OpenAICredentials.DoesNotExist:
            logger.warning(f"Pas de credentials OpenAI valides pour company {company.id}")
            return None
    
    @staticmethod
    def create_or_update_credentials(
        company: Company,
        api_key: str,
        monthly_budget_usd: float = 100.00,
        key_name: str = "Production"
    ) -> OpenAICredentials:
        """Crée ou met à jour les credentials"""
        
        credentials, created = OpenAICredentials.objects.get_or_create(
            company=company,
            defaults={
                'key_name': key_name,
                'monthly_budget_usd': monthly_budget_usd,
                'is_active': True
            }
        )
        
        # Chiffrer et stocker la clé
        credentials.set_api_key(api_key)
        credentials.monthly_budget_usd = monthly_budget_usd
        credentials.key_name = key_name
        credentials.save()
        
        # Valider la clé
        if credentials.validate_key():
            logger.info(f"Credentials OpenAI {'créées' if created else 'mises à jour'} pour {company.name}")
        else:
            logger.error(f"Credentials OpenAI invalides pour {company.name}")
            
        return credentials
    
    @staticmethod
    def validate_all_credentials():
        """Valide toutes les credentials actives"""
        credentials = OpenAICredentials.objects.filter(is_active=True)
        
        results = []
        for cred in credentials:
            is_valid = cred.validate_key()
            results.append({
                'company': cred.company.name,
                'valid': is_valid,
                'status': cred.validation_status
            })
        
        return results
    
    @staticmethod
    def check_budget_for_company(company: Company, estimated_cost: float) -> bool:
        """Vérifie le budget pour une opération"""
        credentials = CredentialsService.get_credentials_for_company(company)
        if not credentials:
            return False
        
        return credentials.check_budget(estimated_cost)
    
    @staticmethod
    def migrate_from_legacy(company: Company) -> Optional[OpenAICredentials]:
        """Migre depuis l'ancien système (company.chatgpt_key)"""
        if not company.chatgpt_key:
            return None
        
        try:
            credentials = CredentialsService.create_or_update_credentials(
                company=company,
                api_key=company.chatgpt_key,
                key_name="Migrated from legacy"
            )
            
            logger.info(f"Credentials migrées pour {company.name}")
            return credentials
            
        except Exception as e:
            logger.error(f"Erreur migration credentials {company.name}: {str(e)}")
            return None
