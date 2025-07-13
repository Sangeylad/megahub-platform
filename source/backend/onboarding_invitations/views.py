# backend/onboarding_invitations/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
import logging

from common.permissions.business_permissions import IsBrandMember, IsBrandAdmin
from brands_core.models import Brand
from .models import UserInvitation
from .services.invitation import (
    send_invitation, accept_invitation, get_invitation_status,
    resend_invitation, get_company_invitations
)
from .serializers import (
    InvitationCreateSerializer, InvitationSerializer,
    InvitationAcceptSerializer, InvitationStatusSerializer
)

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBrandAdmin])
def send_user_invitation(request):
    """
    Envoie invitation utilisateur
    """
    user = request.user
    
    if not user.company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Valider données
        serializer = InvitationCreateSerializer(
            data=request.data,
            context={'company': user.company}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'Données invalides',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer brand
        brand_id = serializer.validated_data['brand_id']
        try:
            brand = Brand.objects.get(id=brand_id, company=user.company)
        except Brand.DoesNotExist:
            return Response({
                'error': 'Brand non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Envoyer invitation
        invitation = send_invitation(
            invited_by=user,
            company=user.company,
            brand=brand,
            email=serializer.validated_data['email'],
            user_type=serializer.validated_data['user_type'],
            message=serializer.validated_data.get('invitation_message', '')
        )
        
        # Sérialiser réponse
        response_serializer = InvitationSerializer(invitation)
        
        return Response({
            'success': True,
            'message': 'Invitation envoyée avec succès',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur envoi invitation par {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur envoi invitation',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_user_invitation(request):
    """
    Accepte invitation utilisateur
    """
    user = request.user
    
    # Valider données
    serializer = InvitationAcceptSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'error': 'Token invalide',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Accepter invitation
        invitation = accept_invitation(
            token=serializer.validated_data['token'],
            user=user
        )
        
        # Recharger user pour avoir company updated
        user.refresh_from_db()
        
        return Response({
            'success': True,
            'message': 'Invitation acceptée avec succès',
            'data': {
                'company_id': user.company.id,
                'company_name': user.company.name,
                'brand_id': invitation.invited_brand.id,
                'brand_name': invitation.invited_brand.name,
                'user_type': user.user_type
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur acceptation invitation par {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur acceptation invitation',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def invitation_status(request, token):
    """
    Status invitation via token (endpoint public)
    """
    try:
        status_data = get_invitation_status(token)
        serializer = InvitationStatusSerializer(status_data)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur status invitation {token}: {str(e)}")
        return Response({
            'error': 'Erreur récupération status',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBrandAdmin])
def resend_user_invitation(request, invitation_id):
    """
    Renvoie invitation
    """
    user = request.user
    
    try:
        invitation = resend_invitation(invitation_id, user)
        
        response_serializer = InvitationSerializer(invitation)
        
        return Response({
            'success': True,
            'message': 'Invitation renvoyée avec succès',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur renvoi invitation {invitation_id} par {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur renvoi invitation',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsBrandMember])
def list_company_invitations(request):
    """
    Liste invitations company
    """
    user = request.user
    
    if not user.company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Filtres
        status_filter = request.query_params.get('status')
        
        # Récupérer invitations
        invitations = get_company_invitations(user.company, status_filter)
        
        # Sérialiser
        serializer = InvitationSerializer(invitations, many=True)
        
        return Response({
            'success': True,
            'data': {
                'invitations': serializer.data,
                'total': invitations.count()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur liste invitations pour {user.username}: {str(e)}")
        return Response({
            'error': 'Erreur récupération invitations',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsBrandAdmin])
def validate_invitation_slots(request):
    """
    Valide slots disponibles pour invitation
    """
    user = request.user
    
    if not user.company:
        return Response({
            'error': 'User sans company'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        emails = request.data.get('emails', [])
        
        if not emails or not isinstance(emails, list):
            return Response({
                'error': 'Liste emails requise'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation via service
        from .services.validation import validate_invitation_slots
        
        validate_invitation_slots(user.company, emails)
        
        return Response({
            'success': True,
            'message': 'Slots disponibles pour invitations',
            'data': {
                'emails_count': len(emails),
                'company_slots': user.company.slots.get_available_users_slots()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Validation slots échouée',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
