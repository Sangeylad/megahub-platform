# backend/onboarding_trials/serializers.py
from rest_framework import serializers
from .models import TrialEvent

class TrialEventSerializer(serializers.ModelSerializer):
    """Serializer pour TrialEvent"""
    
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    triggered_by_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = TrialEvent
        fields = [
            'id', 'event_type', 'event_type_display',
            'event_data', 'processed', 'created_at',
            'triggered_by_name', 'company_name'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_triggered_by_name(self, obj):
        if obj.triggered_by:
            return obj.triggered_by.get_full_name() or obj.triggered_by.username
        return None

class TrialStatusSerializer(serializers.Serializer):
    """Serializer pour status trial"""
    
    is_trial = serializers.BooleanField()
    trial_expires_at = serializers.DateTimeField()
    days_remaining = serializers.IntegerField()
    events_count = serializers.IntegerField()
    can_extend = serializers.BooleanField()

class TrialExtensionSerializer(serializers.Serializer):
    """Serializer pour extension trial"""
    
    additional_weeks = serializers.IntegerField(
        min_value=1,
        max_value=4,
        default=1,
        help_text="Semaines supplémentaires (1-4)"
    )

class UpgradeRequestSerializer(serializers.Serializer):
    """Serializer pour demande upgrade"""
    
    plan_type = serializers.ChoiceField(
        choices=[
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        help_text="Type de plan pour upgrade"
    )
