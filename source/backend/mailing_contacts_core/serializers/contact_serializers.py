# /var/www/megahub/source/backend/mailing_contacts_core/serializers/contact_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer, StatsMixin
from ..models import EmailSubscriber

class EmailSubscriberListSerializer(DynamicFieldsSerializer):
    """Liste abonnés - champs essentiels"""
    brand_name = serializers.CharField(source='source_brand.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    engagement_status = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailSubscriber
        fields = [
            'id', 'email', 'full_name', 'status', 'source', 
            'brand_name', 'engagement_status', 'created_at'
        ]
    
    def get_full_name(self, obj):
        """Nom complet de l'abonné"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return ""
    
    def get_engagement_status(self, obj):
        """Statut d'engagement simplifié"""
        if hasattr(obj, 'subscribertracking'):
            score = obj.subscribertracking.engagement_score
            if score >= 0.7:
                return "high"
            elif score >= 0.3:
                return "medium"
            return "low"
        return "unknown"

class EmailSubscriberDetailSerializer(StatsMixin, DynamicFieldsSerializer):
    """Détail complet abonné avec relations"""
    brand_name = serializers.CharField(source='source_brand.name', read_only=True)
    crm_contact_name = serializers.CharField(source='crm_contact.full_name', read_only=True)
    preferences = serializers.SerializerMethodField()
    tracking_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailSubscriber
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        stats_fields = {
            'lists_count': 'get_lists_count',
            'campaigns_sent': 'get_campaigns_sent',
            'total_opens': 'get_total_opens',
            'total_clicks': 'get_total_clicks'
        }
    
    def get_preferences(self, obj):
        """Préférences de l'abonné"""
        if hasattr(obj, 'subscriberpreferences'):
            prefs = obj.subscriberpreferences
            return {
                'email_marketing': prefs.email_marketing,
                'frequency': prefs.frequency,
                'gdpr_consent': prefs.gdpr_consent,
            }
        return None
    
    def get_tracking_stats(self, obj):
        """Stats de tracking"""
        if hasattr(obj, 'subscribertracking'):
            tracking = obj.subscribertracking
            return {
                'engagement_score': float(tracking.engagement_score),
                'total_emails_sent': tracking.total_emails_sent,
                'total_emails_opened': tracking.total_emails_opened,
                'total_emails_clicked': tracking.total_emails_clicked,
                'last_activity_date': tracking.last_activity_date,
                'is_engaged': tracking.is_engaged,
            }
        return None

class EmailSubscriberWriteSerializer(DynamicFieldsSerializer):
    """Serializer pour création/modification"""
    
    class Meta:
        model = EmailSubscriber
        fields = [
            'email', 'first_name', 'last_name', 'company', 
            'phone', 'source', 'language', 'timezone', 'source_brand'
        ]
    
    def validate_email(self, value):
        """Validation email unique par brand"""
        if self.instance:
            # Update - exclure l'instance actuelle
            qs = EmailSubscriber.objects.filter(
                email=value,
                source_brand=self.initial_data.get('source_brand')
            ).exclude(pk=self.instance.pk)
        else:
            # Create
            qs = EmailSubscriber.objects.filter(
                email=value,
                source_brand=self.initial_data.get('source_brand')
            )
        
        if qs.exists():
            raise serializers.ValidationError(
                "Un abonné avec cet email existe déjà pour cette marque."
            )
        return value