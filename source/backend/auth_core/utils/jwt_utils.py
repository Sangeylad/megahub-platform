# backend/auth_core/utils/jwt_utils.py

import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class JWTUtils:
    """Utilitaires pour les tokens JWT"""
    
    @staticmethod
    def decode_token(token):
        """Décode un token JWT sans validation"""
        try:
            return jwt.decode(
                token, 
                options={"verify_signature": False}
            )
        except jwt.DecodeError:
            return None
    
    @staticmethod
    def get_user_id_from_token(token):
        """Extrait l'ID utilisateur d'un token"""
        payload = JWTUtils.decode_token(token)
        if payload:
            return payload.get('user_id')
        return None
    
    @staticmethod
    def is_token_valid(token):
        """Vérifie si un token est valide"""
        try:
            UntypedToken(token)
            return True
        except (InvalidToken, TokenError):
            return False
    
    @staticmethod
    def get_token_expiry(token):
        """Récupère la date d'expiration d'un token"""
        payload = JWTUtils.decode_token(token)
        if payload:
            exp = payload.get('exp')
            if exp:
                import datetime
                return datetime.datetime.fromtimestamp(exp)
        return None
