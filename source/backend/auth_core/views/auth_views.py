# backend/auth_core/views/auth_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from auth_core.serializers.auth_serializers import (
    LoginSerializer, LoginResponseSerializer, RefreshTokenSerializer,
    UserProfileSerializer, ChangePasswordSerializer, LogoutSerializer
)
from auth_core.services.auth_service import AuthService
from common.views.mixins import AnalyticsViewSetMixin

class AuthViewSet(AnalyticsViewSetMixin, viewsets.GenericViewSet):
    """
    ViewSet pour l'authentification
    
    Endpoints:
    - POST /auth/login/ - Connexion utilisateur
    - POST /auth/logout/ - Déconnexion utilisateur
    - POST /auth/refresh/ - Refresh du token JWT
    - GET /auth/me/ - Profil utilisateur actuel
    - PATCH /auth/me/ - Mise à jour profil
    - POST /auth/change-password/ - Changement mot de passe
    """
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action in ['login', 'refresh']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Sélectionne le serializer selon l'action"""
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'refresh':
            return RefreshTokenSerializer
        elif self.action in ['me', 'update_profile']:
            return UserProfileSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'logout':
            return LogoutSerializer
        return LoginSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        POST /auth/login/
        
        Connexion utilisateur avec JWT
        Body: {"username": "...", "password": "...", "remember_me": false}
        """
        serializer = self.get_serializer(data=request.data)
        
        # Récupérer informations client
        client_ip = AuthService.get_client_ip(request)
        user_agent = AuthService.get_user_agent(request)
        username = request.data.get('username', '')
        
        # Vérifier rate limiting
        rate_limit = AuthService.check_rate_limiting(username, client_ip)
        if rate_limit['email_blocked'] or rate_limit['ip_blocked']:
            # Logger la tentative bloquée
            AuthService.log_login_attempt(
                email=username,
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason="Rate limited"
            )
            
            return Response({
                'error': 'Trop de tentatives de connexion. Réessayez plus tard.',
                'retry_after': 15  # minutes
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Créer les tokens JWT
            tokens = AuthService.create_tokens_for_user(user)
            
            # Mettre à jour les infos de connexion
            AuthService.update_user_login_info(user, client_ip)
            
            # Logger la tentative réussie
            AuthService.log_login_attempt(
                email=username,
                ip_address=client_ip,
                user_agent=user_agent,
                success=True,
                user=user
            )
            
            # Préparer la réponse
            response_data = {
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': user
            }
            
            response_serializer = LoginResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        else:
            # Logger la tentative échouée
            AuthService.log_login_attempt(
                email=username,
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason="Invalid credentials"
            )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        POST /auth/logout/
        
        Déconnexion utilisateur
        Body: {"refresh": "..."} (optionnel)
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Déconnexion réussie'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        """
        POST /auth/refresh/
        
        Refresh du token JWT
        Body: {"refresh": "..."}
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh']
            
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                
                return Response({
                    'access': new_access_token
                }, status=status.HTTP_200_OK)
                
            except (TokenError, InvalidToken):
                return Response({
                    'error': 'Refresh token invalide'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        GET /auth/me/
        
        Profil de l'utilisateur actuel
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """
        PATCH /auth/me/
        
        Mise à jour du profil utilisateur
        Body: {"first_name": "...", "last_name": "...", ...}
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        POST /auth/change-password/
        
        Changement de mot de passe
        Body: {
            "current_password": "...",
            "new_password": "...", 
            "new_password_confirm": "..."
        }
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'user': request.user}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Mot de passe changé avec succès'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def login_history(self, request):
        """
        GET /auth/login-history/
        
        Historique des connexions de l'utilisateur
        """
        from auth_core.models.auth_models import LoginAttempt
        
        attempts = LoginAttempt.objects.filter(
            email=request.user.email
        ).order_by('-created_at')[:20]
        
        history = []
        for attempt in attempts:
            history.append({
                'timestamp': attempt.created_at,
                'ip_address': attempt.ip_address,
                'success': attempt.success,
                'user_agent': attempt.user_agent,
                'failure_reason': attempt.failure_reason
            })
        
        return Response({
            'login_history': history
        }, status=status.HTTP_200_OK)
