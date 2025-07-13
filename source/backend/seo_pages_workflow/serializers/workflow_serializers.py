# backend/seo_pages_workflow/serializers/workflow_serializers.py

from rest_framework import serializers
from django.utils import timezone

from .base_serializers import PageWorkflowBaseSerializer
from ..models import PageStatus, PageWorkflowHistory, PageScheduling

class PageStatusSerializer(PageWorkflowBaseSerializer):
    """Serializer statut workflow des pages"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.SerializerMethodField()
    next_possible_statuses = serializers.SerializerMethodField()
    changed_by_username = serializers.CharField(source='status_changed_by.username', read_only=True)
    can_be_published = serializers.SerializerMethodField()
    
    class Meta:
        model = PageStatus
        fields = [
            'id', 'page', 'page_title', 'page_url',
            'status', 'status_display', 'status_color',
            'status_changed_at', 'status_changed_by', 'changed_by_username',
            'production_notes', 'next_possible_statuses', 'can_be_published'
        ]
    
    def get_status_color(self, obj):
        return obj.get_status_color()
    
    def get_next_possible_statuses(self, obj):
        return obj.get_next_possible_statuses()
    
    def get_can_be_published(self, obj):
        return obj.can_be_published()

class PageStatusUpdateSerializer(PageWorkflowBaseSerializer):
    """Serializer pour mise à jour statut avec notes"""
    
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = PageStatus
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        """Valider transition de statut"""
        if self.instance:
            current_status = self.instance.status
            allowed_transitions = self.instance.get_next_possible_statuses()
            
            if value not in allowed_transitions:
                raise serializers.ValidationError(
                    f"Transition {current_status} → {value} non autorisée. "
                    f"Transitions possibles : {', '.join(allowed_transitions)}"
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Mise à jour avec traçabilité"""
        new_status = validated_data.get('status', instance.status)
        notes = validated_data.get('notes', '')
        user = self.context.get('request').user if self.context.get('request') else None
        
        instance.update_status(new_status, user, notes)
        return instance

class PageWorkflowHistorySerializer(PageWorkflowBaseSerializer):
    """Serializer historique workflow"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = PageWorkflowHistory
        fields = [
            'id', 'page', 'page_title', 'old_status', 'new_status',
            'changed_by', 'changed_by_username', 'notes', 'created_at'
        ]

class PageSchedulingSerializer(PageWorkflowBaseSerializer):
    """Serializer programmation publication"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    is_ready_to_publish = serializers.SerializerMethodField()
    time_until_publish = serializers.SerializerMethodField()
    
    class Meta:
        model = PageScheduling
        fields = [
            'id', 'page', 'page_title', 'scheduled_publish_date',
            'auto_publish', 'is_ready_to_publish', 'time_until_publish'
        ]
    
    def get_is_ready_to_publish(self, obj):
        return obj.is_ready_to_publish()
    
    def get_time_until_publish(self, obj):
        if not obj.scheduled_publish_date:
            return None
        
        now = timezone.now()
        if obj.scheduled_publish_date <= now:
            return "Ready to publish"
        
        delta = obj.scheduled_publish_date - now
        hours = delta.total_seconds() / 3600
        
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)} minutes"
        elif hours < 24:
            return f"{int(hours)} heures"
        else:
            return f"{int(hours / 24)} jours"
    
    def validate_scheduled_publish_date(self, value):
        """Validation date programmée"""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "La date de publication doit être dans le futur"
            )
        return value

class PageWorkflowDashboardSerializer(serializers.Serializer):
    """Serializer dashboard workflow avec stats"""
    
    total_pages = serializers.IntegerField()
    pages_by_status = serializers.DictField()
    recent_changes = PageWorkflowHistorySerializer(many=True)
    scheduled_pages = PageSchedulingSerializer(many=True)
    pages_ready_to_publish = serializers.IntegerField()
