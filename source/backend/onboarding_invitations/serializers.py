# backend/onboarding_invitations/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import UserInvitation
from .services.validation import validate_invitation_data

User = get_user_model()

class InvitationCreateSerializer(serializers.Serializer):
    """Serializer pour création invitation"""
    
    email = serializers.EmailField()
    brand_id = serializers.IntegerField()
    user_type = serializers.ChoiceField(
        choices=[
            ('brand_member', 'Membre Marque'),
            ('brand_admin', 'Admin Marque'),
        ],
        default='brand_member'
    )
    invitation_message = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
    
    def validate(self, attrs):
        """Validation globale"""
        email = attrs['email']
        user_type = attrs['user_type']
        
        # Récupérer brand depuis context (passé par view)
        brand = self.context.get('brand')
        company = self.context.get('company')
        
        if not brand or not company:
            raise serializers.ValidationError("Brand et Company requis dans context")
        
        # Validation métier
        validate_invitation_data(email, user_type, company, brand)
        
        return attrs

class InvitationSerializer(serializers.ModelSerializer):
    """Serializer pour UserInvitation"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    brand_name = serializers.CharField(source='invited_brand.name', read_only=True)
    invited_by_name = serializers.SerializerMethodField()
    accepted_by_name = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserInvitation
        fields = [
            'id', 'email', 'status', 'user_type',
            'company_name', 'brand_name',
            'invited_by_name', 'accepted_by_name',
            'expires_at', 'accepted_at', 'created_at',
            'is_valid', 'is_expired',
            'invitation_message'
        ]
        read_only_fields = ['id', 'status', 'accepted_at', 'created_at']
    
    def get_invited_by_name(self, obj):
        return obj.invited_by.get_full_name() or obj.invited_by.username
    
    def get_accepted_by_name(self, obj):
        if obj.accepted_by:
            return obj.accepted_by.get_full_name() or obj.accepted_by.username
        return None
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_is_expired(self, obj):
        return obj.is_expired()

class InvitationAcceptSerializer(serializers.Serializer):
    """Serializer pour acceptation invitation"""
    
    token = serializers.UUIDField()
    
    def validate_token(self, value):
        """Valide token existence"""
        try:
            invitation = UserInvitation.objects.get(token=value)
            self.invitation = invitation  # Store for use in view
            return value
        except UserInvitation.DoesNotExist:
            raise serializers.ValidationError("Token d'invitation invalide")

class InvitationStatusSerializer(serializers.Serializer):
    """Serializer pour status invitation"""
    
    found = serializers.BooleanField()
    invitation = serializers.DictField(required=False)
    error = serializers.CharField(required=False)