# backend/onboarding_business/services/roles_setup.py

import logging

logger = logging.getLogger(__name__)


def assign_default_roles(user, company, brand):
    """
    Assigne les rôles par défaut à un user
    
    Args:
        user (CustomUser): User à configurer
        company (Company): Company associée
        brand (Brand): Brand associée
        
    Returns:
        list: Liste des UserRole créés
    """
    try:
        from users_roles.models import Role, UserRole
        
        created_roles = []
        
        # Rôles par défaut pour owner business
        default_roles = [
            ('company_admin', 'company'),    # Admin company
            ('brand_admin', 'brand'),        # Admin brand
            ('websites_admin', 'feature')    # Admin websites feature
        ]
        
        for role_name, role_context in default_roles:
            try:
                role = Role.objects.get(name=role_name, is_active=True)
                
                # Définir contexte selon type rôle
                context_kwargs = {'granted_by': user}
                
                if role_context == 'company':
                    context_kwargs.update({'company': company})
                elif role_context == 'brand':
                    context_kwargs.update({'company': company, 'brand': brand})
                elif role_context == 'feature':
                    context_kwargs.update({'company': company, 'brand': brand})
                
                user_role = UserRole.objects.create(
                    user=user,
                    role=role,
                    **context_kwargs
                )
                
                created_roles.append(user_role)
                logger.debug(f"Rôle {role_name} assigné à {user.username}")
                
            except Role.DoesNotExist:
                logger.warning(f"Rôle {role_name} non trouvé - skip")
                continue
            except Exception as e:
                logger.error(f"Erreur assignation rôle {role_name} à {user.username}: {str(e)}")
                continue
        
        logger.info(f"Rôles assignés pour {user.username}: {len(created_roles)} rôles")
        return created_roles
        
    except ImportError:
        logger.info("users_roles non disponible - skip roles assignment")
        return []
    except Exception as e:
        logger.error(f"Erreur setup rôles pour {user.username}: {str(e)}")
        return []


def get_user_roles_summary(user):
    """
    Résumé des rôles pour un user
    
    Args:
        user (CustomUser): User à analyser
        
    Returns:
        dict: Résumé des rôles
    """
    try:
        from users_roles.models import UserRole
        
        user_roles = user.user_roles.filter(
            role__is_active=True
        ).select_related('role', 'company', 'brand').order_by('role__role_type', 'role__name')
        
        return {
            'total_roles': user_roles.count(),
            'roles': [
                {
                    'name': ur.role.name,
                    'display_name': ur.role.display_name,
                    'role_type': ur.role.role_type,
                    'context': ur.get_context_summary(),
                    'is_active': ur.is_active(),
                    'granted_at': ur.granted_at
                }
                for ur in user_roles
            ]
        }
        
    except ImportError:
        return {'total_roles': 0, 'roles': []}
    except Exception as e:
        logger.error(f"Erreur résumé rôles pour {user.username}: {str(e)}")
        return {'total_roles': 0, 'roles': [], 'error': str(e)}