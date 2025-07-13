# backend/blog_publishing/serializers/publishing_serializers.py

from rest_framework import serializers
from django.utils import timezone
from common.serializers.mixins import TimestampedSerializer
from common.serializers.mixins import StatsMixin
from common.serializers.mixins import StatsMixin
from ..models import BlogPublishingStatus, BlogScheduledPublication


class BlogPublishingStatusSerializer(TimestampedSerializer):
    """Statut publication avec workflow"""
    
    # Champs Article read-only
    article_title = serializers.CharField(source='article.page.title', read_only=True)
    article_author = serializers.CharField(source='article.primary_author.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    # Propriétés calculées
    is_published_now = serializers.BooleanField(source='is_published', read_only=True)
    can_publish = serializers.BooleanField(source='can_be_published', read_only=True)
    is_scheduled_future = serializers.BooleanField(source='is_scheduled', read_only=True)
    
    class Meta:
        model = BlogPublishingStatus
        fields = '__all__'
        
        field_config = {
            'list': [
                'id', 'article_title', 'article_author', 'status',
                'published_date', 'scheduled_date', 'is_featured',
                'is_published_now', 'can_publish'
            ],
            'detail': '__all__',
            'create': ['article', 'status', 'scheduled_date'],
            'update': [
                'status', 'published_date', 'scheduled_date',
                'is_featured', 'is_premium', 'is_evergreen',
                'notify_on_publish'
            ]
        }
        
        admin_only_fields = ['approved_by', 'approved_at']
        read_only_fields = ['created_at', 'updated_at', 'submitted_for_review_at']
    
    def validate(self, attrs):
        """Validation workflow states"""
        status = attrs.get('status')
        scheduled_date = attrs.get('scheduled_date')
        
        # Si programmé, date obligatoire
        if status == 'scheduled' and not scheduled_date:
            raise serializers.ValidationError({
                'scheduled_date': 'Date obligatoire pour articles programmés'
            })
        
        # Date programmée dans le futur
        if scheduled_date and scheduled_date <= timezone.now():
            raise serializers.ValidationError({
                'scheduled_date': 'La date doit être dans le futur'
            })
        
        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        """Gestion workflow automatique"""
        status = validated_data.get('status')
        
        if status == 'published' and not instance.published_date:
            validated_data['published_date'] = timezone.now()
            validated_data['last_published_date'] = timezone.now()
        
        if status == 'pending_review' and not instance.submitted_for_review_at:
            validated_data['submitted_for_review_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class BlogScheduledPublicationSerializer(TimestampedSerializer):
    """Publications programmées"""
    
    article_title = serializers.CharField(source='article.page.title', read_only=True)
    scheduled_by_name = serializers.CharField(source='scheduled_by.get_full_name', read_only=True)
    
    # Propriétés calculées
    is_ready = serializers.BooleanField(source='is_ready_for_execution', read_only=True)
    can_retry_now = serializers.BooleanField(source='can_retry', read_only=True)
    
    class Meta:
        model = BlogScheduledPublication
        fields = '__all__'
        
        field_config = {
            'list': [
                'id', 'article_title', 'scheduled_for', 'execution_status',
                'scheduled_by_name', 'is_ready', 'retry_count'
            ],
            'detail': '__all__'
        }
        
        read_only_fields = [
            'created_at', 'updated_at', 'executed_at', 'error_message', 
            'retry_count', 'scheduled_by'
        ]
    
    def create(self, validated_data):
        """Auto-assign scheduled_by"""
        validated_data['scheduled_by'] = self.context['request'].user
        return super().create(validated_data)