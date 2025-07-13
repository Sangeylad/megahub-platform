# backend/ai_providers/services/credential_service.py

import logging
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from typing import Optional, Dict, Any

from ..models import AICredentials, AIProvider

logger = logging.getLogger(__name__)

class CredentialService:
    """Service sécurisé pour credentials IA"""
    
    def __init__(self):
        # Clé encryption depuis settings
        encryption_key = getattr(settings, 'AI_ENCRYPTION_KEY', None)
        if not encryption_key:
            raise ImproperlyConfigured("AI_ENCRYPTION_KEY required in settings")
        
        # ✅ FIX : Utilise directement la clé générée par Fernet
        try:
            # La clé vient de Fernet.generate_key().decode() donc c'est déjà du base64 valide
            self.cipher = Fernet(encryption_key.encode())
        except Exception as e:
            logger.error(f"Erreur initialisation Fernet: {e}")
            raise ImproperlyConfigured(f"AI_ENCRYPTION_KEY invalide: {e}")
    
    def encrypt_credential(self, credential: str) -> str:
        """Chiffrer une credential"""
        if not credential:
            return ""
        return self.cipher.encrypt(credential.encode()).decode()
    
    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Déchiffrer une credential"""
        if not encrypted_credential:
            return ""
        try:
            return self.cipher.decrypt(encrypted_credential.encode()).decode()
        except Exception as e:
            logger.error(f"Erreur déchiffrement credential: {e}")
            return ""
    
    def get_credentials_for_company(self, company) -> Dict[str, str]:
        """Récupérer toutes les credentials déchiffrées"""
        try:
            ai_creds = AICredentials.objects.get(company=company)
        except AICredentials.DoesNotExist:
            return {}
        
        return {
            'openai': self.decrypt_credential(ai_creds.openai_api_key),
            'anthropic': self.decrypt_credential(ai_creds.anthropic_api_key),
            'google': self.decrypt_credential(ai_creds.google_api_key),
        }
    
    def set_credential_for_company(
        self, 
        company, 
        provider_name: str, 
        api_key: str
    ) -> bool:
        """Définir credential pour un provider"""
        ai_creds, created = AICredentials.objects.get_or_create(company=company)
        
        encrypted_key = self.encrypt_credential(api_key)
        
        if provider_name == 'openai':
            ai_creds.openai_api_key = encrypted_key
        elif provider_name == 'anthropic':
            ai_creds.anthropic_api_key = encrypted_key
        elif provider_name == 'google':
            ai_creds.google_api_key = encrypted_key
        else:
            logger.error(f"Provider non supporté: {provider_name}")
            return False
        
        ai_creds.save()
        logger.info(f"Credential {provider_name} mise à jour pour {company.name}")
        return True
    
    def get_api_key_for_provider(self, company, provider_name: str) -> Optional[str]:
        """Récupérer clé API déchiffrée pour un provider"""
        credentials = self.get_credentials_for_company(company)
        return credentials.get(provider_name)