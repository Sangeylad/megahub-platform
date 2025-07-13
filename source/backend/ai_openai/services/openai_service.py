# backend/ai_openai/services/openai_service.py

import logging
import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from requests.exceptions import HTTPError, RequestException

from ai_providers.services import CredentialService
from ..models import OpenAIConfig

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service OpenAI moderne avec support O3 et legacy"""
    
    def __init__(self, company=None, config_name: str = 'default'):
        self.company = company
        self.config = self._get_config(config_name)
        self.credential_service = CredentialService()
        
        # API Key dynamique
        if company:
            self.api_key = self.credential_service.get_api_key_for_provider(
                company, 'openai'
            )
        else:
            self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if not self.api_key:
            raise ValueError("OpenAI API key required")
    
    def _get_config(self, config_name: str) -> OpenAIConfig:
        """Récupérer config OpenAI"""
        try:
            return OpenAIConfig.objects.get(name=config_name, is_active=True)
        except OpenAIConfig.DoesNotExist:
            return OpenAIConfig(
                name='default',
                base_url='https://api.openai.com',
                timeout_seconds=300,
                max_retries=3
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers OpenAI"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _is_new_generation_model(self, model: str) -> bool:
        """Détecte modèles nouvelle génération"""
        return model.startswith('o3') or model in ['gpt-4.1']
    
    def _convert_messages_to_structured(self, messages: List[Dict]) -> List[Dict]:
        """Convertit messages legacy vers format structuré"""
        structured_messages = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            # 🎯 MAPPING ROLE POUR O3
            if role == 'system':
                role = 'developer'
            
            # 🎯 STRUCTURE CONTENT POUR NOUVEAUX MODÈLES
            if isinstance(content, str):
                structured_content = [{"type": "text", "text": content}]
            else:
                structured_content = content
            
            structured_messages.append({
                'role': role,
                'content': structured_content
            })
        
        return structured_messages
    
    def _build_payload(
        self,
        messages: List[Dict],
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Construit payload selon le modèle"""
        
        # Détection format
        is_new_gen = self._is_new_generation_model(model)
        
        # Messages
        if is_new_gen:
            formatted_messages = self._convert_messages_to_structured(messages)
        else:
            formatted_messages = messages
        
        # Payload de base
        payload = {
            "model": model,
            "messages": formatted_messages
        }
        
        # 🎯 PARAMÈTRES SELON GÉNÉRATION
        if is_new_gen:
            # Nouveaux modèles (o3, gpt-4.1)
            if kwargs.get('max_tokens'):
                payload["max_completion_tokens"] = kwargs['max_tokens']
            
            if model.startswith('o3'):
                # Spécifique O3
                payload["reasoning_effort"] = kwargs.get('reasoning_effort', 'medium')
            else:
                # gpt-4.1
                payload.update({
                    "temperature": kwargs.get('temperature', 1),
                    "top_p": kwargs.get('top_p', 1),
                    "frequency_penalty": kwargs.get('frequency_penalty', 0),
                    "presence_penalty": kwargs.get('presence_penalty', 0)
                })
        else:
            # Modèles legacy (gpt-4o, gpt-4-turbo)
            payload.update({
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens')
            })
        
        # Paramètres communs
        if kwargs.get('tools'):
            payload["tools"] = kwargs['tools']
        if kwargs.get('tool_resources'):
            payload["tool_resources"] = kwargs['tool_resources']
        if kwargs.get('response_format'):
            payload["response_format"] = kwargs['response_format']
        
        return payload
    
    def _make_request(
        self, 
        endpoint: str, 
        payload: Dict[str, Any], 
        method: str = 'POST'
    ) -> Dict[str, Any]:
        """Requête générique OpenAI"""
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers()
        
        logger.info(f"OpenAI Request to {endpoint} with model {payload.get('model')}")
        
        try:
            if method == 'POST':
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=payload,
                    timeout=self.config.timeout_seconds
                )
            else:
                response = requests.get(
                    url, 
                    headers=headers,
                    timeout=self.config.timeout_seconds
                )
            
            response.raise_for_status()
            return response.json()
            
        except HTTPError as e:
            logger.error(f"OpenAI API error {e.response.status_code}: {e.response.text}")
            raise
        except RequestException as e:
            logger.error(f"OpenAI request error: {str(e)}")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict],
        model: str = 'gpt-4o',
        **kwargs
    ) -> Dict[str, Any]:
        """Chat completion avec support multi-modèles"""
        
        payload = self._build_payload(messages, model, **kwargs)
        
        logger.info(f"Chat completion with {model}, payload structure: {list(payload.keys())}")
        
        return self._make_request("/v1/chat/completions", payload)