# backend/onboarding_trials/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import logging

from common.permissions.business_permissions import IsCompanyAdmin
from .models import TrialEvent
from .services.trial import (
    get_trial_analytics, extend_trial,
    create_trial_event
)
from .services.auto_upgrade import (
    trigger_manual_upgrade, get_upgrade_opportunities
)
from .services.billing_integration import get_billing_upgrade_summary
from .serializers import (
    TrialEventSerializer, TrialStatusSerializer,
    TrialExtensionSerializer, UpgradeRequestSerializer
)

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def trial_status(request):
    """
    Status complet du trial
    """
    user = request.user
    
    if not user.company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analytics = get_trial_analytics(user.company)
        
        return Response({
            'success': True,
            'data': analytics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur trial_status pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur récupération trial status',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsCompanyAdmin])
def extend_trial_period(request):
    """
    Étend la période de trial
    """
    user = request.user
    company = user.company
    
    if not company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Valider données
    serializer = TrialExtensionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'error': 'Données invalides',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        additional_weeks = serializer.validated_data['additional_weeks']
        
        success = extend_trial(company, additional_weeks, triggered_by=user)
        
        if success:
            return Response({
                'success': True,
                'message': f'Trial étendu de {additional_weeks} semaine(s)',
                'data': {
                    'new_expires_at': company.trial_expires_at,
                    'days_remaining': company.trial_days_remaining()
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Extension trial impossible',
                'details': 'Company pas en trial ou déjà expirée'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Erreur extension trial pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur extension trial',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def trial_events(request):
    """
    Liste des événements trial
    """
    user = request.user
    
    if not user.company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        events = user.company.trial_events.order_by('-created_at')
        
        # Filtrage optionnel
        event_type = request.query_params.get('event_type')
        if event_type:
            events = events.filter(event_type=event_type)
        
        # Pagination simple
        limit = int(request.query_params.get('limit', 20))
        events = events[:limit]
        
        serializer = TrialEventSerializer(events, many=True)
        
        return Response({
            'success': True,
            'data': {
                'events': serializer.data,
                'total': user.company.trial_events.count()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur trial_events pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur récupération events',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsCompanyAdmin])
def request_upgrade(request):
    """
    Demande upgrade manuel
    """
    user = request.user
    company = user.company
    
    if not company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Valider données
    serializer = UpgradeRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'error': 'Données invalides',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plan_type = serializer.validated_data['plan_type']
        
        success = trigger_manual_upgrade(company, plan_type, triggered_by=user)
        
        if success:
            return Response({
                'success': True,
                'message': f'Upgrade vers {plan_type} initié',
                'data': {
                    'plan_type': plan_type,
                    'company_mode': company.get_business_mode()
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Upgrade échoué',
                'details': 'Erreur lors du processus upgrade'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Erreur request_upgrade pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur demande upgrade',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def upgrade_detection(request):
    """
    Détection auto-upgrade et opportunities
    """
    user = request.user
    
    if not user.company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        company = user.company
        
        data = {
            'business_mode': company.get_business_mode(),
            'is_solo': company.is_solo_business(),
            'is_agency': company.is_agency(),
            'brands_count': company.brands.filter(is_deleted=False).count(),
            'auto_upgraded': company.trial_events.filter(event_type='auto_upgrade').exists(),
            'upgrade_opportunities': get_billing_upgrade_summary(company)
        }
        
        return Response({
            'success': True,
            'data': data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur upgrade_detection pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur détection upgrade',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)