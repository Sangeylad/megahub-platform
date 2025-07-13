# backend/onboarding_business/serializers/setup.py
"""
Serializers pour le setup business
"""
from rest_framework import serializers
from django.core.validators import MinLengthValidator, MaxLengthValidator
import re

class BusinessSetupSerializer(serializers.Serializer):
    """
    Serializer pour les données de setup business
    """
    business_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        validators=[
            MinLengthValidator(2, message="Le nom du business doit faire au moins 2 caractères"),
            MaxLengthValidator(200, message="Le nom du business ne peut pas dépasser 200 caractères")
        ],
        help_text="Nom du business (optionnel, généré automatiquement si non fourni)"
    )
    
    def validate_business_name(self, value):
        """Validation custom du nom business"""
        if not value:
            return value
        
        # Nettoyer le nom
        value = value.strip()
        
        # Vérifier caractères autorisés (lettres, chiffres, espaces, certains caractères spéciaux)
        if not re.match(r'^[a-zA-Z0-9\s\-_&\.\'\"]+$', value):
            raise serializers.ValidationError(
                "Le nom du business ne peut contenir que des lettres, chiffres, espaces et caractères spéciaux basiques"
            )
        
        # Pas que des espaces
        if not value.replace(' ', '').replace('-', '').replace('_', ''):
            raise serializers.ValidationError(
                "Le nom du business ne peut pas être vide ou ne contenir que des espaces"
            )
        
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Si business_name fourni mais vide après nettoyage
        business_name = data.get('business_name', '').strip()
        if business_name == '':
            data['business_name'] = None
        else:
            data['business_name'] = business_name
        
        return data

class BusinessStatusSerializer(serializers.Serializer):
    """
    Serializer pour le status d'onboarding (lecture seule)
    """
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_eligible_for_business = serializers.BooleanField(read_only=True)
    has_business = serializers.BooleanField(read_only=True)
    onboarding_complete = serializers.BooleanField(read_only=True)
    business_summary = serializers.DictField(read_only=True)

class BusinessSetupResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse de création business (documentation API)
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()
    
    class Meta:
        # Pour documentation swagger/openapi
        example = {
            "success": True,
            "message": "Business créé avec succès",
            "data": {
                "company_id": 1,
                "company_name": "John's Business",
                "brand_id": 1,
                "brand_name": "John's Brand",
                "is_trial": True,
                "trial_days_remaining": 14,
                "slots_info": {
                    "users_slots": 1,
                    "brands_slots": 10
                }
            }
        }

class BusinessEligibilitySerializer(serializers.Serializer):
    """
    Serializer pour vérification d'éligibilité
    """
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_eligible = serializers.BooleanField(read_only=True)
    has_existing_business = serializers.BooleanField(read_only=True)
    ineligibility_reason = serializers.CharField(read_only=True, required=False)