# backend/ai_openai/models/provider_models.py

from django.db import models
from django.core.exceptions import ValidationError
from common.models.mixins import TimestampedMixin
from cryptography.fernet import Fernet
from django.conf import settings
import base64

class OpenAIProvider(TimestampedMixin):
    """Configuration globale du provider OpenAI"""
    
    name = models.CharField(max_length=100, default="OpenAI")
    base_url = models.URLField(default="https://api.openai.com")
    is_active = models.BooleanField(default=True)
    
    # Limites globales
    daily_request_limit = models.IntegerField(default=10000)
    daily_cost_limit_usd = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    
    class Meta:
        db_table = 'openai_provider'
        verbose_name = "Provider OpenAI"
    
    def __str__(self):
        return f"{self.name} ({'Actif' if self.is_active else 'Inactif'})"

class OpenAICredentials(TimestampedMixin):
    """Credentials OpenAI chiffrées par company"""
    
    company = models.OneToOneField(
        'company_core.Company', 
        on_delete=models.CASCADE,
        related_name='openai_credentials'
    )
    
    # Clé chiffrée
    encrypted_api_key = models.TextField()
    
    # Métadonnées
    key_name = models.CharField(max_length=100, default="Production")
    is_active = models.BooleanField(default=True)
    
    # Quotas par company
    monthly_budget_usd = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    current_month_usage_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Validation
    last_validated_at = models.DateTimeField(null=True, blank=True)
    validation_status = models.CharField(
        max_length=20,
        choices=[
            ('valid', 'Valide'),
            ('invalid', 'Invalide'),
            ('expired', 'Expirée'),
            ('quota_exceeded', 'Quota dépassé')
        ],
        default='valid'
    )
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'openai_credentials'
        verbose_name = "Credentials OpenAI"
        verbose_name_plural = "Credentials OpenAI"
    
    def __str__(self):
        return f"OpenAI - {self.company.name} ({self.key_name})"
    
    def _get_encryption_key(self):
        """Récupère la clé de chiffrement"""
        key = getattr(settings, 'AI_ENCRYPTION_KEY', None)
        if not key:
            raise ValidationError("AI_ENCRYPTION_KEY not configured")
        return base64.urlsafe_b64decode(key)
    
    def set_api_key(self, api_key: str):
        """Chiffre et stocke la clé API"""
        fernet = Fernet(self._get_encryption_key())
        self.encrypted_api_key = fernet.encrypt(api_key.encode()).decode()
    
    def get_api_key(self) -> str:
        """Déchiffre et retourne la clé API"""
        fernet = Fernet(self._get_encryption_key())
        return fernet.decrypt(self.encrypted_api_key.encode()).decode()
    
    def validate_key(self) -> bool:
        """Valide la clé via un appel API test"""
        try:
            # TODO: Implémenter validation avec AIService
            from brands_core.services.ai_service import AIService
            ai_service = AIService(api_key=self.get_api_key())
            
            # Test simple
            response = ai_service.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
                model="gpt-3.5-turbo",
                max_tokens=1
            )
            
            self.validation_status = 'valid'
            self.last_validated_at = timezone.now()
            self.save(update_fields=['validation_status', 'last_validated_at'])
            return True
            
        except Exception:
            self.validation_status = 'invalid'
            self.save(update_fields=['validation_status'])
            return False
    
    def check_budget(self, estimated_cost: float) -> bool:
        """Vérifie si le budget permet l'opération"""
        return (self.current_month_usage_usd + estimated_cost) <= self.monthly_budget_usd
    
    def add_usage(self, cost_usd: float):
        """Ajoute un coût à l'usage mensuel"""
        self.current_month_usage_usd += cost_usd
        if self.current_month_usage_usd >= self.monthly_budget_usd:
            self.validation_status = 'quota_exceeded'
        self.save(update_fields=['current_month_usage_usd', 'validation_status'])
