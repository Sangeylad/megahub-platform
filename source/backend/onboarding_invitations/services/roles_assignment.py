# backend/onboarding_invitations/services/roles_assignment.py
import logging

logger = logging.getLogger(__name__)

def assign_invitation_roles(user, invitation):
    """
    Assigne les rôles pour user qui accepte invitation
    
    Args:
        user (CustomUser): User qui a accepté
        invitation (UserInvitation): Invitation acceptée
        
    Returns:
        list: Rôles assignés
    """
    try:
        from users_roles.models import Role, UserRole
        
        created_roles = []
        
        # Rôles selon user_type
        if invitation.user_type == 'brand_admin':
            role_names = ['brand_admin', 'websites_admin']
        else:  # brand_member
            role_names = ['brand_member', 'websites_editor']
        
        for role_name in role_names:
            try:
                role = Role.objects.get(name=role_name, is_active=True)
                
                user_role = UserRole.objects.create(
                    user=user,
                    role=role,
                    company=invitation.company,
                    brand=invitation.invited_brand,
                    granted_by=invitation.invited_by
                )
                
                created_roles.append(user_role)
                logger.debug(f"Rôle {role_name} assigné à {user.username}")
                
            except Role.DoesNotExist:
                logger.warning(f"Rôle {role_name} non trouvé - skip")
                continue
        
        logger.info(f"Rôles assignés pour invitation {user.username}: {len(created_roles)} rôles")
        return created_roles
        
    except ImportError:
        logger.info("users_roles non disponible - skip roles assignment")
        return []
    except Exception as e:
        logger.error(f"Erreur assignment rôles invitation {user.username}: {str(e)}")
        return []

def get_invitation_available_roles():
    """
    Rôles disponibles pour invitations
    
    Returns:
        dict: Rôles par user_type
    """
    try:
        from users_roles.models import Role
        
        return {
            'brand_member': [
                'brand_member',
                'websites_editor'
            ],
            'brand_admin': [
                'brand_admin', 
                'websites_admin'
            ]
        }
        
    except ImportError:
        return {}