# backend/task_persistence/serializers/persistent_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from task_core.serializers import BaseTaskSerializer
from ..models import PersistentJob, JobCheckpoint, JobState

class JobStateSerializer(serializers.ModelSerializer):
    """Serializer pour JobState"""
    
    class Meta:
        model = JobState
        fields = '__all__'

class PersistentJobSerializer(DynamicFieldsSerializer):
    """Serializer complet pour PersistentJob"""
    
    base_task = BaseTaskSerializer(read_only=True)
    job_state = JobStateSerializer(read_only=True)
    latest_checkpoint = serializers.SerializerMethodField()
    
    class Meta:
        model = PersistentJob
        fields = '__all__'
        read_only_fields = ['progress_percentage', 'last_checkpoint_at']
    
    def get_latest_checkpoint(self, obj):
        """Retourne le dernier checkpoint"""
        checkpoint = obj.get_latest_checkpoint()
        if checkpoint:
            return JobCheckpointSerializer(checkpoint).data
        return None

class JobCheckpointSerializer(serializers.ModelSerializer):
    """Serializer pour JobCheckpoint"""
    
    class Meta:
        model = JobCheckpoint
        fields = '__all__'
        read_only_fields = ['created_at']
