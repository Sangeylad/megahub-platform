# backend/ai_providers/views/provider_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import AIProvider, AICredentials
from ..serializers import AIProviderSerializer, AICredentialsSerializer
from ..services import CredentialService, QuotaService

class AIProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """Providers IA disponibles"""
    queryset = AIProvider.objects.filter(is_active=True)
    serializer_class = AIProviderSerializer
    permission_classes = [IsAuthenticated]

class AICredentialsViewSet(viewsets.ModelViewSet):
    """Gestion credentials IA par company"""
    queryset = AICredentials.objects.all()
    serializer_class = AICredentialsSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    
    def get_queryset(self):
        # Filtrer par company de l'user
        user = self.request.user
        if hasattr(user, 'company'):
            return self.queryset.filter(company=user.company)
        return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def quota_status(self, request):
        """GET /providers/credentials/quota_status/?provider=openai"""
        provider_name = request.query_params.get('provider', 'openai')
        
        if not hasattr(request.user, 'company'):
            return Response(
                {'error': 'Company required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quota_status = QuotaService.get_quota_status(
            request.user.company, 
            provider_name
        )
        return Response(quota_status)
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """POST /providers/credentials/test_connection/ {"provider": "openai"}"""
        provider_name = request.data.get('provider')
        if not provider_name:
            return Response(
                {'error': 'Provider required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not hasattr(request.user, 'company'):
            return Response(
                {'error': 'Company required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer clé API
        credential_service = CredentialService()
        api_key = credential_service.get_api_key_for_provider(
            request.user.company, 
            provider_name
        )
        
        if not api_key:
            return Response(
                {'success': False, 'error': 'No API key configured'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Tester connexion réelle selon provider
        return Response({
            'success': True, 
            'message': f'Connection to {provider_name} successful'
        })
