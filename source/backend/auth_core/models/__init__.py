# backend/auth_core/models/__init__.py

# Utilise les modèles existants de users_core
from users_core.models.user import CustomUser

__all__ = ['CustomUser']
