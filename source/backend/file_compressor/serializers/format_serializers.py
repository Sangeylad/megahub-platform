# backend/file_compressor/serializers/format_serializers.py
from rest_framework import serializers
from ..models import CompressionFormat

class CompressionFormatSerializer(serializers.ModelSerializer):
    """Serializer simple pour les formats de compression"""
    
    class Meta:
        model = CompressionFormat
        fields = [
            'id', 'name', 'extension', 'mime_type', 'category',
            'compression_ratio', 'is_active', 'supports_password',
            'supports_encryption', 'max_file_size'
        ]
        read_only_fields = ['id']

class CompressionFormatDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les formats"""
    
    max_file_size_mb = serializers.SerializerMethodField()
    average_compression_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = CompressionFormat
        fields = [
            'id', 'name', 'extension', 'mime_type', 'category',
            'compression_ratio', 'average_compression_percentage',
            'is_active', 'supports_password', 'supports_encryption',
            'max_file_size', 'max_file_size_mb'
        ]
    
    def get_max_file_size_mb(self, obj):
        return obj.max_file_size // (1024 * 1024)
    
    def get_average_compression_percentage(self, obj):
        return (1 - obj.compression_ratio) * 100