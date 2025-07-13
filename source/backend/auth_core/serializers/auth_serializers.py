# backend/auth_core/serializers/auth_serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from users_core.models.user import CustomUser
from common.serializers.mixins import DynamicFieldsSerializer

class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    
    username = serializers.CharField(
        help_text="Nom d'utilisateur ou email"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Mot de passe"
    )
    remember_me = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Se souvenir de moi"
    )
    
    def validate(self, data):
        """Validation et authentification"""
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username et password requis")
        
        # Supporter email ou username
        user = None
        if '@' in username:
            # C'est un email
            try:
                user_obj = CustomUser.objects.get(email=username, is_active=True)
                username = user_obj.username
            except CustomUser.DoesNotExist:
                pass
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError("Identifiants invalides")
        
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé")
        
        data['user'] = user
        return data

class LoginResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de connexion"""
    
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Retourne les données utilisateur"""
        user = obj['user']
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
            'company': {
                'id': user.company.id,
                'name': user.company.name
            } if user.company else None,
            'permissions_summary': user.get_permissions_summary(),
        }

class RefreshTokenSerializer(serializers.Serializer):
    """Serializer pour le refresh token"""
    
    refresh = serializers.CharField(
        help_text="Refresh token"
    )
    
    def validate_refresh(self, value):
        """Valide le refresh token"""
        try:
            token = RefreshToken(value)
            # Vérifier si le token est valide
            token.check_blacklist()
            return value
        except Exception:
            raise serializers.ValidationError("Refresh token invalide")

class UserProfileSerializer(DynamicFieldsSerializer):
    """Serializer pour le profil utilisateur"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    permissions_summary = serializers.SerializerMethodField()
    accessible_brands_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone', 'position', 'company', 'company_name',
            'can_access_analytics', 'can_access_reports',
            'permissions_summary', 'accessible_brands_info',
            'last_login', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'user_type', 'company', 'company_name',
            'last_login', 'date_joined', 'created_at', 'updated_at'
        ]
    
    def get_permissions_summary(self, obj):
        """Résumé des permissions"""
        return obj.get_permissions_summary()
    
    def get_accessible_brands_info(self, obj):
        """Informations sur les marques accessibles"""
        brands = obj.get_accessible_brands()
        return {
            'count': brands.count(),
            'names': [brand.name for brand in brands[:5]]
        }

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    
    current_password = serializers.CharField(
        write_only=True,
        help_text="Mot de passe actuel"
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="Nouveau mot de passe"
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        help_text="Confirmation du nouveau mot de passe"
    )
    
    def validate_current_password(self, value):
        """Vérifie le mot de passe actuel"""
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect")
        return value
    
    def validate(self, data):
        """Validation globale"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Les mots de passe ne correspondent pas'
            })
        return data
    
    def save(self):
        """Sauvegarde le nouveau mot de passe"""
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class LogoutSerializer(serializers.Serializer):
    """Serializer pour la déconnexion"""
    
    refresh = serializers.CharField(
        required=False,
        help_text="Refresh token à blacklister"
    )
    
    def validate_refresh(self, value):
        """Valide le refresh token"""
        if value:
            try:
                token = RefreshToken(value)
                return value
            except Exception:
                raise serializers.ValidationError("Refresh token invalide")
        return value
    
    def save(self):
        """Blacklist le refresh token"""
        refresh_token = self.validated_data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # Token déjà blacklisté ou invalide
