# backend/auth_core/services/auth_service.py

from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from auth_core.models.auth_models import LoginAttempt
from users_core.models.user import CustomUser

class AuthService:
    """Service d'authentification"""
    
    @staticmethod
    def create_tokens_for_user(user):
        """Crée les tokens JWT pour un utilisateur"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def log_login_attempt(email, ip_address, user_agent, success=True, 
                         failure_reason=None, user=None):
        """Enregistre une tentative de connexion"""
        return LoginAttempt.objects.create(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason or ""
        )
    
    @staticmethod
    def check_rate_limiting(email, ip_address, window_minutes=15, max_attempts=5):
        """Vérifie les limitations de tentatives de connexion"""
        window_start = timezone.now() - timezone.timedelta(minutes=window_minutes)
        
        # Compter les échecs récents par email
        email_failures = LoginAttempt.objects.filter(
            email=email,
            success=False,
            created_at__gte=window_start
        ).count()
        
        # Compter les échecs récents par IP
        ip_failures = LoginAttempt.objects.filter(
            ip_address=ip_address,
            success=False,
            created_at__gte=window_start
        ).count()
        
        return {
            'email_blocked': email_failures >= max_attempts,
            'ip_blocked': ip_failures >= max_attempts * 3,  # Plus permissif pour IP
            'email_attempts': email_failures,
            'ip_attempts': ip_failures,
            'max_attempts': max_attempts
        }
    
    @staticmethod
    def update_user_login_info(user, ip_address):
        """Met à jour les informations de dernière connexion"""
        user.last_login = timezone.now()
        user.last_login_ip = ip_address
        user.save(update_fields=['last_login', 'last_login_ip'])
    
    @staticmethod
    def blacklist_refresh_token(refresh_token):
        """Blacklist un refresh token"""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_client_ip(request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_agent(request):
        """Récupère le user agent"""
        return request.META.get('HTTP_USER_AGENT', '')[:500]  # Limiter la taille
