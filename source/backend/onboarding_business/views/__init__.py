# backend/onboarding_business/views/__init__.py

from .setup import (
    BusinessSetupView,
    BusinessSetupStatusView,
    trigger_business_creation,
    check_setup_eligibility
)

# Views stats manquantes (pour compléter urls.py)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def business_stats(request):
    """GET /onboarding/business/stats/"""
    user = request.user
    
    # ✅ FIX : Retourner 404 au lieu de 400 pour user sans company
    if not hasattr(user, 'company') or not user.company:
        return Response({
            'success': False,
            'error': 'User sans company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    company = user.company
    
    try:
        # Utiliser get_stats_summary si disponible
        if hasattr(company, 'get_stats_summary'):
            stats = company.get_stats_summary()
        else:
            # Fallback manuel
            stats = {
                'business_mode': company.get_business_mode() if hasattr(company, 'get_business_mode') else 'unknown',
                'is_trial': company.is_in_trial() if hasattr(company, 'is_in_trial') else False,
                'trial_days_remaining': company.trial_days_remaining() if hasattr(company, 'trial_days_remaining') else 0,
                'brands_count': company.brands.filter(is_deleted=False).count() if hasattr(company, 'brands') else 0,
                'users_count': company.members.filter(is_active=True).count() if hasattr(company, 'members') else 0
            }
        
        return Response({
            'success': True,
            'data': {'company_stats': stats}
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Erreur récupération stats',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def features_summary(request):
    """GET /onboarding/business/features-summary/"""
    user = request.user
    
    # ✅ FIX : Retourner 404 au lieu de 400 pour user sans company
    if not hasattr(user, 'company') or not user.company:
        return Response({
            'success': False,
            'error': 'User sans company'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Import optionnel du service features
        try:
            from ..services.features_setup import get_company_features_summary
            features = get_company_features_summary(user.company)
        except ImportError:
            # Fallback si service pas disponible
            features = {
                'total_features': 0,
                'active_features': 0,
                'features_by_type': {},
                'error': 'Service features_setup non disponible'
            }
        
        return Response({
            'success': True,
            'data': features
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Erreur récupération features',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

__all__ = [
    'BusinessSetupView',
    'BusinessSetupStatusView', 
    'trigger_business_creation',
    'check_setup_eligibility',
    'business_stats',
    'features_summary'
]