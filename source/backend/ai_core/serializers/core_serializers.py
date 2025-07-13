# backend/ai_core/serializers/core_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer

from ..models import AIJob, AIJobType

class AIJobTypeSerializer(DynamicFieldsSerializer):
    """Serializer types de jobs IA"""
    
    class Meta:
        model = AIJobType
        fields = '__all__'

class AIJobSerializer(DynamicFieldsSerializer):
    """Serializer jobs IA"""
    job_type_name = serializers.CharField(source='job_type.name', read_only=True)
    job_type_category = serializers.CharField(source='job_type.category', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    # ✅ Permettre job_type comme string en écriture
    job_type = serializers.CharField(write_only=True, required=False, help_text="Nom du job type")
    
    class Meta:
        model = AIJob
        fields = '__all__'
        read_only_fields = ['job_id', 'status', 'started_at', 'completed_at', 'brand', 'created_by']
        field_config = {
            'list': [
                'id', 'job_id', 'job_type_name', 'status', 
                'progress_percentage', 'created_at', 'brand_name'
            ],
            'retrieve': '__all__'
        }
    
    def get_duration_seconds(self, obj):
        """Calcul durée execution"""
        if obj.started_at and obj.completed_at:
            return int((obj.completed_at - obj.started_at).total_seconds())
        return None