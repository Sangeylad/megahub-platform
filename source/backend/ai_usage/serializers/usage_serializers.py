# backend/ai_usage/serializers/usage_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer

from ..models import AIJobUsage, AIUsageAlert

class AIJobUsageSerializer(DynamicFieldsSerializer):
   """Serializer usage jobs IA"""
   ai_job_id = serializers.CharField(source='ai_job.job_id', read_only=True)
   ai_job_type = serializers.CharField(source='ai_job.job_type.name', read_only=True)
   cost_per_token = serializers.SerializerMethodField()
   
   class Meta:
       model = AIJobUsage
       fields = '__all__'
       read_only_fields = ['ai_job']
   
   def get_cost_per_token(self, obj):
       """Coût par token"""
       if obj.total_tokens > 0:
           return float(obj.total_cost / obj.total_tokens)
       return 0

class AIUsageAlertSerializer(DynamicFieldsSerializer):
   """Serializer alertes usage"""
   company_name = serializers.CharField(source='company.name', read_only=True)
   days_since_created = serializers.SerializerMethodField()
   
   class Meta:
       model = AIUsageAlert
       fields = '__all__'
       read_only_fields = ['company']
   
   def get_days_since_created(self, obj):
       """Jours depuis création"""
       from django.utils import timezone
       delta = timezone.now() - obj.created_at
       return delta.days
