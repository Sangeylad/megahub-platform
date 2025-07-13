# backend/auth_core/utils/validators.py

import re
from django.core.exceptions import ValidationError

class AuthValidators:
    """Validateurs pour l'authentification"""
    
    @staticmethod
    def validate_password_strength(password):
        """Valide la force d'un mot de passe"""
        errors = []
        
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        
        if not re.search(r'[a-z]', password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")
        
        if not re.search(r'\d', password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def validate_username(username):
        """Valide un nom d'utilisateur"""
        if not username:
            raise ValidationError("Le nom d'utilisateur est requis")
        
        if len(username) < 3:
            raise ValidationError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        
        if len(username) > 30:
            raise ValidationError("Le nom d'utilisateur ne peut pas dépasser 30 caractères")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores")
        
        return True
    
    @staticmethod
    def validate_email_format(email):
        """Valide le format d'un email"""
        if not email:
            raise ValidationError("L'email est requis")
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("Format d'email invalide")
        
        return True
