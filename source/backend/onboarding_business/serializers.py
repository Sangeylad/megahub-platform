# backend/onboarding_business/serializers.py

from rest_framework import serializers
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model
import re

from common.serializers.mixins import DynamicFieldsSerializer
from company_core.models import Company
from brands_core.models import Brand

User = get_user_model()


class BusinessSetupSerializer(serializers.Serializer):
    """Serializer pour le setup business explicite"""
    
    business_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        validators=[
            MinLengthValidator(2, message="Le nom du business doit faire au moins 2 caractères"),
            MaxLengthValidator(255, message="Le nom du business ne peut pas dépasser 255 caractères")
        ],
        help_text="Nom du business (optionnel, généré automatiquement si non fourni)"
    )
    
    def validate_business_name(self, value):
        """Validation custom du nom business"""
        if not value:
            return value
            
        # Nettoyer le nom
        value = value.strip()
        
        # Vérifier caractères autorisés
        if not re.match(r'^[a-zA-Z0-9\s\-&\.\'\"À-ÿ]+$', value):
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
        business_name = data.get('business_name', '').strip() if data.get('business_name') else None
        if business_name == '':
            data['business_name'] = None
        else:
            data['business_name'] = business_name
            
        return data


class BusinessStatusSerializer(DynamicFieldsSerializer):
    """Serializer pour le status d'onboarding complet"""
    
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_eligible_for_business = serializers.BooleanField(read_only=True)
    has_business = serializers.BooleanField(read_only=True)
    onboarding_complete = serializers.BooleanField(read_only=True)
    business_summary = serializers.DictField(read_only=True)
    
    class Meta:
        fields = [
            'user_id', 'username', 'is_eligible_for_business', 
            'has_business', 'onboarding_complete', 'business_summary'
        ]


class BusinessStatsSerializer(DynamicFieldsSerializer):
    """Serializer pour les stats détaillées du business"""
    
    company_stats = serializers.DictField(read_only=True)
    slots_usage = serializers.DictField(read_only=True) 
    features_summary = serializers.DictField(read_only=True)
    trial_summary = serializers.DictField(read_only=True)
    user_roles = serializers.DictField(read_only=True)
    permissions_summary = serializers.DictField(read_only=True)
    
    class Meta:
        fields = [
            'company_stats', 'slots_usage', 'features_summary',
            'trial_summary', 'user_roles', 'permissions_summary'
        ]


class BusinessSetupResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de création business"""
    
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
                "company_name": "Mon Business",
                "brand_id": 1,
                "brand_name": "Ma Brand",
                "is_trial": True,
                "trial_days_remaining": 14,
                "business_mode": "solo",
                "slots_info": {
                    "users_slots": 1,
                    "brands_slots": 10
                }
            }
        }


class CompanyStatsSerializer(DynamicFieldsSerializer):
    """Serializer pour stats company"""
    
    business_mode = serializers.CharField(read_only=True)
    is_in_trial = serializers.BooleanField(read_only=True)
    trial_days_remaining = serializers.IntegerField(read_only=True)
    brands_stats = serializers.DictField(read_only=True)
    users_stats = serializers.DictField(read_only=True)
    
    class Meta:
        fields = ['business_mode', 'is_in_trial', 'trial_days_remaining', 'brands_stats', 'users_stats']


class BusinessEligibilitySerializer(serializers.Serializer):
    """Serializer pour vérification d'éligibilité"""
    
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_eligible = serializers.BooleanField(read_only=True)
    has_existing_business = serializers.BooleanField(read_only=True)
    ineligibility_reason = serializers.CharField(read_only=True, required=False)
    can_setup_business = serializers.BooleanField(read_only=True)
    
    
    
class BusinessSummarySerializer(DynamicFieldsSerializer):
    """Serializer pour résumé business creation"""
    
    has_business = serializers.BooleanField(read_only=True)
    company = serializers.DictField(read_only=True, required=False)
    brands = serializers.ListField(read_only=True, required=False)
    stats = serializers.DictField(read_only=True, required=False)
    permissions = serializers.DictField(read_only=True, required=False)
    
    class Meta:
        fields = ['has_business', 'company', 'brands', 'stats', 'permissions']


class BusinessCreationRequestSerializer(serializers.Serializer):
    """Serializer pour request création business"""
    
    business_name = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Nom du business (optionnel)"
    )
    
    def validate_business_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Le nom du business doit faire au moins 2 caractères")
        return value.strip() if value else None


class OnboardingStatusSerializer(serializers.Serializer):
    """Serializer pour status onboarding global"""
    
    user_eligible = serializers.BooleanField(read_only=True)
    business_exists = serializers.BooleanField(read_only=True)
    setup_complete = serializers.BooleanField(read_only=True)
    next_steps = serializers.ListField(read_only=True)
    business_mode = serializers.CharField(read_only=True, required=False)