# backend/onboarding_invitations/services/validation.py
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
import logging

from ..models import UserInvitation

logger = logging.getLogger(__name__)

def validate_invitation_permissions(user, company, brand):
    """
    Valide les permissions pour envoyer invitation
    
    Args:
        user (CustomUser): User qui invite
        company (Company): Company d'invitation
        brand (Brand): Brand concernée
        
    Raises:
        PermissionDenied: Si permissions insuffisantes
    """
    # User doit être company admin ou brand admin
    if not user.can_invite_users():
        raise PermissionDenied("Permissions insuffisantes pour inviter")
    
    # Vérifier que user a accès à cette company
    if user.company != company:
        raise PermissionDenied("User n'appartient pas à cette company")
    
    # Vérifier accès à la brand
    if not user.can_access_brand(brand):
        raise PermissionDenied("User n'a pas accès à cette brand")
    
    # Brand doit appartenir à la company
    if brand.company != company:
        raise ValidationError("Brand n'appartient pas à cette company")

def validate_invitation_slots(company, invited_emails):
    """
    Valide que company a assez de slots pour invitations
    
    Args:
        company (Company): Company concernée
        invited_emails (list): Liste emails à inviter
        
    Raises:
        ValidationError: Si slots insuffisants
    """
    if not company.can_add_user():
        raise ValidationError(
            f"Limite utilisateurs atteinte ({company.slots.current_users_count}/{company.slots.users_slots})"
        )
    
    # Compter invitations pending
    pending_invitations = UserInvitation.objects.filter(
        company=company,
        status='pending',
        expires_at__gt=timezone.now()
    ).count()
    
    # Calculer total besoin
    total_needed = len(invited_emails) + pending_invitations
    available_slots = company.slots.get_available_users_slots()
    
    if total_needed > available_slots:
        raise ValidationError(
            f"Pas assez de slots disponibles. "
            f"Besoin: {total_needed} (nouvelles: {len(invited_emails)}, pending: {pending_invitations}), "
            f"Disponibles: {available_slots}"
        )

def validate_invitation_data(email, user_type, company, brand):
    """
    Valide les données d'invitation
    
    Args:
        email (str): Email à inviter
        user_type (str): Type user
        company (Company): Company
        brand (Brand): Brand
        
    Raises:
        ValidationError: Si données invalides
    """
    # Vérifier email format (Django le fait déjà mais...)
    from django.core.validators import validate_email
    validate_email(email)
    
    # Vérifier que user n'existe pas déjà dans company
    from users_core.models import CustomUser
    
    existing_user = CustomUser.objects.filter(
        email=email,
        company=company
    ).first()
    
    if existing_user:
        raise ValidationError(f"User {email} déjà membre de {company.name}")
    
    # Vérifier user_type valide
    valid_types = ['brand_member', 'brand_admin']
    if user_type not in valid_types:
        raise ValidationError(f"user_type invalide. Valides: {valid_types}")

def validate_invitation_acceptance(invitation, user):
    """
    Valide l'acceptation d'invitation
    
    Args:
        invitation (UserInvitation): Invitation à accepter
        user (CustomUser): User qui accepte
        
    Raises:
        ValidationError: Si acceptance invalide
    """
    # Invitation valide
    if not invitation.is_valid():
        raise ValidationError("Invitation expirée ou déjà utilisée")
    
    # Email correspond
    if user.email != invitation.email:
        raise ValidationError("Email user ne correspond pas à l'invitation")
    
    # User pas déjà assigné
    if user.company is not None:
        raise ValidationError(f"User déjà assigné à company {user.company.name}")
    
    # Company peut encore ajouter user
    if not invitation.company.can_add_user():
        raise ValidationError("Company a atteint sa limite d'utilisateurs")