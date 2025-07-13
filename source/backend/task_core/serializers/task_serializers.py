# backend/task_core/serializers/task_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import BaseTask

class BaseTaskListSerializer(DynamicFieldsSerializer):
    """Serializer allégé pour les listes"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = BaseTask
        fields = [
            'id', 'task_id', 'task_type', 'status', 'priority',
            'created_at', 'created_by_name', 'description'
        ]

class BaseTaskSerializer(DynamicFieldsSerializer):
    """Serializer complet pour les détails"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = BaseTask
        fields = '__all__'
        read_only_fields = [
            'task_id', 'celery_task_id', 'created_at', 'updated_at',
            'brand', 'created_by'  # ✅ AJOUT : Auto-assignés par perform_create
        ]