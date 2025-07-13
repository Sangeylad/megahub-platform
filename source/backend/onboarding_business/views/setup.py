# backend/onboarding_business/views/setup.py

"""
Views pour le setup business explicite
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import logging

from ..services.onboarding import OnboardingService
# ✅ FIX : Supprimé import inexistant get_business_creation_summary
from ..serializers import BusinessSetupSerializer

logger = logging.getLogger(__name__)

class BusinessSetupView(APIView):
    """
    Endpoint principal pour setup business explicite
    Remplace l'ancien système de signal automatique
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /onboarding/business/setup/
        
        Crée un business pour l'utilisateur connecté
        """
        user = request.user
        
        # Vérifier éligibilité
        if not OnboardingService.is_user_eligible_for_business(user):
            return Response({
                'success': False,
                'error': 'User non éligible pour création business',
                'details': self._get_ineligibility_reason(user)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation des données
        serializer = BusinessSetupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Données invalides',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                result = OnboardingService.setup_business_for_user(
                    user=user,
                    business_name=serializer.validated_data.get('business_name')
                )
                
            logger.info(f"Business setup via API pour {user.username}")
            
            return Response({
                'success': True,
                'message': 'Business créé avec succès',
                'data': {
                    'company_id': result['company'].id,
                    'company_name': result['company'].name,
                    'brand_id': result['brand'].id,
                    'brand_name': result['brand'].name,
                    'is_trial': result['company'].is_in_trial(),
                    'trial_days_remaining': result['company'].trial_days_remaining(),
                    'slots_info': {
                        'users_slots': result['slots'].users_slots,
                        'brands_slots': result['slots'].brands_slots
                    }
                }
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.warning(f"Validation error setup business pour {user.username}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Erreur de validation',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Erreur setup business pour {user.username}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Erreur lors de la création business',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_ineligibility_reason(self, user):
        """Helper pour détailler pourquoi user non éligible"""
        if user.company is not None:
            return f"User déjà assigné à la company '{user.company.name}'"
        
        if user.is_staff:
            return "Les utilisateurs staff ne peuvent pas créer de business"
        
        if user.is_superuser:
            return "Les super-utilisateurs ne peuvent pas créer de business"
        
        if not user.is_active:
            return "L'utilisateur n'est pas actif"
        
        return "Raison inconnue"

class BusinessSetupStatusView(APIView):
    """
    Endpoint pour vérifier le status d'onboarding d'un utilisateur
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /onboarding/business/setup-status/
        
        Retourne le status complet d'onboarding
        """
        user = request.user
        # ✅ FIX : Utiliser la méthode qui existe
        status_data = OnboardingService.get_user_business_status(user)
        
        return Response({
            'success': True,
            'data': status_data
        }, status=status.HTTP_200_OK)

# ====== FONCTION VIEWS POUR COMPATIBILITÉ ======

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_business_creation(request):
    """
    Endpoint de compatibilité pour trigger manuel
    Utilise maintenant OnboardingService
    """
    user = request.user
    
    # ✅ FIX : Utiliser la méthode qui existe
    if not OnboardingService.is_user_eligible_for_business(user):
        return Response({
            'success': False,
            'error': 'User non éligible pour création business',
            'details': 'User déjà assigné à une company ou contraintes non respectées'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            result = OnboardingService.setup_business_for_user(
                user=user, 
                business_name=request.data.get('business_name')
            )
            
        logger.info(f"Business créé via trigger manuel pour {user.username}")
        
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
        logger.error(f"Erreur trigger business pour {user.username}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Erreur lors de la création business',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_setup_eligibility(request):
    """
    Endpoint pour vérifier l'éligibilité sans créer
    """
    user = request.user
    is_eligible = OnboardingService.is_user_eligible_for_business(user)
    
    response_data = {
        'success': True,
        'data': {
            'user_id': user.id,
            'username': user.username,
            'is_eligible': is_eligible,
            'has_existing_business': user.company is not None
        }
    }
    
    if not is_eligible:
        response_data['data']['ineligibility_reason'] = BusinessSetupView()._get_ineligibility_reason(user)
    
    return Response(response_data, status=status.HTTP_200_OK)