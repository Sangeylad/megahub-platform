# backend/onboarding_invitations/services/invitation.py
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

from ..models import UserInvitation
from .validation import validate_invitation_slots, validate_invitation_permissions
from .email import send_invitation_email

logger = logging.getLogger(__name__)

def send_invitation(invited_by, company, brand, email, user_type='brand_member', message=''):
    """
    Envoie une invitation utilisateur
    
    Args:
        invited_by (CustomUser): User qui invite
        company (Company): Company d'invitation
        brand (Brand): Brand spécifique
        email (str): Email invité
        user_type (str): Type user à assigner
        message (str): Message personnalisé
        
    Returns:
        UserInvitation: Invitation créée
        
    Raises:
        ValidationError: Si validation échoue
    """
    # Validations préalables
    validate_invitation_permissions(invited_by, company, brand)
    validate_invitation_slots(company, [email])
    
    # Vérifier invitation existante
    existing = UserInvitation.objects.filter(
        company=company,
        email=email,
        status='pending'
    ).first()
    
    if existing:
        if existing.is_valid():
            raise ValidationError(f"Invitation pending déjà existante pour {email}")
        else:
            # Expirée, on peut la renouveler
            existing.mark_as_expired()
    
    with transaction.atomic():
        # Créer nouvelle invitation
        invitation = UserInvitation.objects.create(
            company=company,
            invited_brand=brand,
            invited_by=invited_by,
            email=email,
            user_type=user_type,
            invitation_message=message
        )
        
        # Envoyer email
        send_invitation_email(invitation)
        
        logger.info(f"Invitation envoyée: {email} -> {brand.name} par {invited_by.username}")
        
        return invitation

def accept_invitation(token, user):
    """
    Accepte une invitation via token
    
    Args:
        token (str): Token d'invitation
        user (CustomUser): User qui accepte
        
    Returns:
        UserInvitation: Invitation acceptée
        
    Raises:
        ValidationError: Si acceptance invalide
    """
    try:
        invitation = UserInvitation.objects.get(token=token)
    except UserInvitation.DoesNotExist:
        raise ValidationError("Invitation non trouvée")
    
    # Accepter invitation (logique dans model)
    invitation.accept(user)
    
    logger.info(f"Invitation acceptée: {user.username} rejoint {invitation.invited_brand.name}")
    
    return invitation

def get_invitation_status(token):
    """
    Status d'une invitation via token
    
    Args:
        token (str): Token d'invitation
        
    Returns:
        dict: Status de l'invitation
    """
    try:
        invitation = UserInvitation.objects.select_related(
            'company', 'invited_brand', 'invited_by'
        ).get(token=token)
        
        return {
            'found': True,
            'invitation': invitation.get_summary()
        }
        
    except UserInvitation.DoesNotExist:
        return {
            'found': False,
            'error': 'Invitation non trouvée'
        }

def resend_invitation(invitation_id, user):
    """
    Renvoie une invitation
    
    Args:
        invitation_id (int): ID invitation
        user (CustomUser): User qui renvoie
        
    Returns:
        UserInvitation: Invitation renvoyée
    """
    try:
        invitation = UserInvitation.objects.get(id=invitation_id)
        
        # Vérifier permissions
        validate_invitation_permissions(user, invitation.company, invitation.invited_brand)
        
        # Renouveler
        invitation.resend()
        
        logger.info(f"Invitation renvoyée: {invitation.email} par {user.username}")
        
        return invitation
        
    except UserInvitation.DoesNotExist:
        raise ValidationError("Invitation non trouvée")

def get_company_invitations(company, status=None):
    """
    Liste des invitations d'une company
    
    Args:
        company (Company): Company concernée
        status (str, optional): Filtrer par status
        
    Returns:
        QuerySet: Invitations
    """
    invitations = UserInvitation.objects.filter(
        company=company
    ).select_related('invited_brand', 'invited_by', 'accepted_by').order_by('-created_at')
    
    if status:
        invitations = invitations.filter(status=status)
    
    return invitations

def cleanup_expired_invitations():
    """
    Nettoie les invitations expirées (task périodique)
    
    Returns:
        int: Nombre d'invitations nettoyées
    """
    expired_invitations = UserInvitation.objects.filter(
        status='pending',
        expires_at__lt=timezone.now()
    )
    
    count = expired_invitations.count()
    expired_invitations.update(status='expired')
    
    logger.info(f"Invitations expirées nettoyées: {count}")
    return count