# backend/onboarding_registration/views.py
# onboarding_registration/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
import logging

from .services.validation import can_trigger_business_creation

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_business_creation(request):
    """
    Endpoint pour déclencher manuellement la création business
    Utile si le signal auto a échoué
    """
    user = request.user
    
    if not can_trigger_business_creation(user):
        return Response({
            'error': 'User non éligible pour création business',
            'details': 'User déjà assigné à une company ou contraintes non respectées'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from onboarding_business.services.business_creation import create_solo_business_for_user
        
        with transaction.atomic():
            result = create_solo_business_for_user(
                user, 
                business_name=request.data.get('business_name')
            )
            
        logger.info(f"Business créé manuellement pour {user.username}")
        
        return Response({
            'success': True,
            'message': 'Business créé avec succès',
            'data': {
                'company_id': result['company'].id,
                'brand_id': result['brand'].id,
                'is_trial': result['company'].is_in_trial()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur création business manuelle pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur lors de la création business',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)