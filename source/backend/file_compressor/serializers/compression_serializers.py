# backend/file_compressor/serializers/compression_serializers.py
from rest_framework import serializers
from ..models import SupportedFileType, FileOptimization, OptimizationQuota

class SupportedFileTypeSerializer(serializers.ModelSerializer):
    max_file_size_mb = serializers.SerializerMethodField()
    average_compression_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportedFileType
        fields = [
            'id', 'name', 'extension', 'mime_type', 'category',
            'average_compression_ratio', 'average_compression_percentage',
            'is_active', 'max_file_size', 'max_file_size_mb',
            'supports_quality_levels', 'supports_resize', 'default_quality'
        ]
    
    def get_max_file_size_mb(self, obj):
        return obj.max_file_size // (1024 * 1024)
    
    def get_average_compression_percentage(self, obj):
        return (1 - obj.average_compression_ratio) * 100

class FileOptimizationSerializer(serializers.ModelSerializer):
    file_type_name = serializers.CharField(source='file_type.name', read_only=True)
    file_type_category = serializers.CharField(source='file_type.category', read_only=True)
    formatted_reduction = serializers.CharField(read_only=True)
    size_reduction_mb = serializers.CharField(read_only=True)
    original_size_mb = serializers.SerializerMethodField()
    optimized_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = FileOptimization
        fields = [
            'id', 'created_at', 'completed_at', 'original_filename', 
            'original_size', 'original_size_mb', 'original_mime_type',
            'file_type', 'file_type_name', 'file_type_category',
            'quality_level', 'custom_quality', 'resize_enabled',
            'target_width', 'target_height', 'maintain_aspect_ratio',
            'status', 'progress', 'error_message',
            'optimized_filename', 'optimized_size', 'optimized_size_mb',
            'compression_ratio', 'size_reduction_bytes', 'size_reduction_percentage',
            'formatted_reduction', 'size_reduction_mb', 'download_url', 'expires_at',
            'optimization_time', 'final_dimensions', 'final_quality',
            'optimization_details'
        ]
        read_only_fields = [
            'id', 'created_at', 'completed_at', 'status', 'progress',
            'error_message', 'optimized_filename', 'optimized_size',
            'compression_ratio', 'size_reduction_bytes', 'size_reduction_percentage',
            'download_url', 'expires_at', 'optimization_time',
            'final_dimensions', 'final_quality', 'optimization_details'
        ]
    
    def get_original_size_mb(self, obj):
        return round(obj.original_size / (1024 * 1024), 2)
    
    def get_optimized_size_mb(self, obj):
        if obj.optimized_size:
            return round(obj.optimized_size / (1024 * 1024), 2)
        return None

class FileOptimizationCreateSerializer(serializers.Serializer):
    """Serializer pour la création d'optimisation"""
    file = serializers.FileField()
    quality_level = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'lossless'],
        default='medium'
    )
    resize_enabled = serializers.BooleanField(default=False)
    target_width = serializers.IntegerField(required=False, min_value=100, max_value=4096)
    target_height = serializers.IntegerField(required=False, min_value=100, max_value=4096)
    maintain_aspect_ratio = serializers.BooleanField(default=True)
    
    def validate_file(self, value):
        """Validation du fichier uploadé"""
        # Taille maximale (sera vérifié aussi dans la vue)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(f"Fichier trop volumineux (max: {max_size // 1024 // 1024}MB)")
        
        # Types MIME supportés
        supported_mimes = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/webp',
            'application/pdf'
        ]
        
        if value.content_type not in supported_mimes:
            raise serializers.ValidationError(f"Type de fichier non supporté: {value.content_type}")
        
        return value
    
    def validate(self, data):
        """Validation croisée"""
        if data.get('resize_enabled'):
            if not data.get('target_width') and not data.get('target_height'):
                raise serializers.ValidationError(
                    "Veuillez spécifier au moins une dimension cible si le redimensionnement est activé"
                )
        
        return data

class OptimizationQuotaSerializer(serializers.ModelSerializer):
    remaining_usage = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    max_file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = OptimizationQuota
        fields = [
            'monthly_limit', 'current_month_usage', 'remaining_usage',
            'usage_percentage', 'max_file_size', 'max_file_size_mb',
            'reset_date', 'can_use_lossless', 'can_resize',
            'can_custom_quality', 'max_resolution'
        ]
        read_only_fields = ['current_month_usage', 'reset_date']
    
    def get_remaining_usage(self, obj):
        return max(0, obj.monthly_limit - obj.current_month_usage)
    
    def get_usage_percentage(self, obj):
        if obj.monthly_limit == 0:
            return 0
        return (obj.current_month_usage / obj.monthly_limit) * 100
    
    def get_max_file_size_mb(self, obj):
        return obj.max_file_size // (1024 * 1024)