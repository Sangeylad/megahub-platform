# backend/ai_openai/views/credentials_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions.business_permissions import IsAuthenticated, IsCompanyAdmin
from ..models import OpenAICredentials
from ..serializers import OpenAICredentialsSerializer
from ..services import CredentialsService

class OpenAICredentialsViewSet(viewsets.ModelViewSet):
    """
    API pour gestion des credentials OpenAI (admin uniquement)
    """
    queryset = OpenAICredentials.objects.all()
    serializer_class = OpenAICredentialsSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    
    def get_queryset(self):
        # Company admin ne voit que ses credentials
        user = self.request.user
        if hasattr(user, 'admin_company'):
            return self.queryset.filter(company=user.admin_company)
        return self.queryset.none()
    
    @action(detail=False, methods=['post'])
    def create_or_update(self, request):
        """Crée ou met à jour les credentials"""
        try:
            company = request.user.admin_company
            data = request.data
            
            credentials = CredentialsService.create_or_update_credentials(
                company=company,
                api_key=data['api_key'],
                monthly_budget_usd=data.get('monthly_budget_usd', 100.00),
                key_name=data.get('key_name', 'Production')
            )
            
            serializer = self.get_serializer(credentials)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valide une clé API"""
        credentials = self.get_object()
        is_valid = credentials.validate_key()
        
        return Response({
            'valid': is_valid,
            'status': credentials.validation_status
        })
    
    @action(detail=False, methods=['post'])
    def migrate_legacy(self, request):
        """Migre depuis l'ancien système"""
        try:
            company = request.user.admin_company
            credentials = CredentialsService.migrate_from_legacy(company)
            
            if credentials:
                serializer = self.get_serializer(credentials)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'No legacy key found or migration failed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
