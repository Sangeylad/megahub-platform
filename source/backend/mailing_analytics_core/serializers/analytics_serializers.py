# /var/www/megahub/backend/mailing_analytics_core/serializers/analytics_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import EmailEvent

class EmailEventListSerializer(DynamicFieldsSerializer):
    """Liste événements - champs essentiels"""
    subscriber_email = serializers.CharField(source='subscriber.email', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    
    class Meta:
        model = EmailEvent
        fields = [
            'id', 'event_type', 'subscriber_email', 'campaign_name',
            'email_address', 'timestamp', 'processed', 'created_at'
        ]

class EmailEventDetailSerializer(DynamicFieldsSerializer):
    """Détail complet événement"""
    subscriber_email = serializers.CharField(source='subscriber.email', read_only=True)
    subscriber_name = serializers.SerializerMethodField()
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    automation_name = serializers.CharField(source='automation.name', read_only=True)
    
    class Meta:
        model = EmailEvent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subscriber_name(self, obj):
        if obj.subscriber:
            return f"{obj.subscriber.first_name} {obj.subscriber.last_name}".strip()
        return ""

class EmailEventCreateSerializer(DynamicFieldsSerializer):
    """Création d'événements via webhook/API"""
    
    class Meta:
        model = EmailEvent
        fields = [
            'event_type', 'subscriber', 'campaign', 'automation',
            'email_address', 'timestamp', 'ip_address', 'user_agent', 'metadata'
        ]
    
    def validate_email_address(self, value):
        """Validation format email"""
        if '@' not in value:
            raise serializers.ValidationError("Format d'email invalide")
        return value.lower()
