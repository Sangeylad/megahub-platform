# backend/onboarding_invitations/services/email.py
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_invitation_email(invitation):
    """
    Envoie email d'invitation
    
    Args:
        invitation (UserInvitation): Invitation à envoyer
        
    Returns:
        bool: True si envoyé avec succès
    """
    try:
        # Structure email template (à implémenter selon besoins)
        subject = f"Invitation à rejoindre {invitation.company.name}"
        
        message = f"""
        Bonjour,
        
        {invitation.invited_by.get_full_name() or invitation.invited_by.username} vous invite à rejoindre 
        la marque "{invitation.invited_brand.name}" chez {invitation.company.name}.
        
        {"Message personnalisé: " + invitation.invitation_message if invitation.invitation_message else ""}
        
        Pour accepter cette invitation, cliquez sur le lien ci-dessous :
        {settings.FRONTEND_URL}{invitation.get_invitation_url()}
        
        Cette invitation expire le {invitation.expires_at.strftime('%d/%m/%Y à %H:%M')}.
        
        Cordialement,
        L'équipe MEGAHUB
        """
        
        # TODO: Intégrer avec système email (Celery + templates HTML)
        logger.info(f"Email invitation préparé pour {invitation.email}")
        
        # Pour l'instant, juste logger (remplacer par vraie logique email)
        logger.info(f"EMAIL TO: {invitation.email}")
        logger.info(f"SUBJECT: {subject}")
        logger.info(f"MESSAGE: {message}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoi email invitation {invitation.email}: {str(e)}")
        return False

def send_invitation_reminder(invitation):
    """
    Envoie rappel invitation
    
    Args:
        invitation (UserInvitation): Invitation pour rappel
        
    Returns:
        bool: True si envoyé
    """
    # TODO: Template rappel spécifique
    logger.info(f"Rappel invitation pour {invitation.email}")
    return send_invitation_email(invitation)

def get_invitation_email_template(invitation):
    """
    Template email d'invitation
    
    Args:
        invitation (UserInvitation): Invitation
        
    Returns:
        dict: Template data
    """
    return {
        'subject': f"Invitation à rejoindre {invitation.company.name}",
        'recipient': invitation.email,
        'template_name': 'invitations/invitation_email.html',
        'context': {
            'invitation': invitation,
            'invited_by': invitation.invited_by,
            'company': invitation.company,
            'brand': invitation.invited_brand,
            'acceptance_url': f"{settings.FRONTEND_URL}{invitation.get_invitation_url()}",
            'expires_at': invitation.expires_at
        }
    }