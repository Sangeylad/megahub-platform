# backend/auth_core/models/auth_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class LoginAttempt(TimestampedMixin):
    """Tentatives de connexion pour sécurité"""
    
    email = models.EmailField(
        help_text="Email de tentative de connexion"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Adresse IP de la tentative"
    )
    success = models.BooleanField(
        default=False,
        help_text="Tentative réussie ou non"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent du navigateur"
    )
    failure_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text="Raison de l'échec si applicable"
    )
    
    class Meta:
        db_table = 'auth_login_attempt'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.email} - {self.created_at}"

class PasswordResetToken(TimestampedMixin):
    """Tokens de réinitialisation de mot de passe"""
    
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text="Utilisateur concerné"
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        help_text="Token de réinitialisation"
    )
    expires_at = models.DateTimeField(
        help_text="Date d'expiration du token"
    )
    used = models.BooleanField(
        default=False,
        help_text="Token utilisé ou non"
    )
    
    class Meta:
        db_table = 'auth_password_reset_token'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'used']),
        ]
    
    def __str__(self):
        return f"Reset token for {self.user.email}"
    
    def is_valid(self):
        """Vérifie si le token est valide"""
        from django.utils import timezone
        return not self.used and timezone.now() <= self.expires_at
