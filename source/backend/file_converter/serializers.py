# backend/file_converter/serializers.py
from rest_framework import serializers
from .models import FileConversion, SupportedFormat, ConversionQuota

class SupportedFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedFormat
        fields = ['name', 'mime_type', 'category', 'is_input', 'is_output']

class FileConversionSerializer(serializers.ModelSerializer):
    input_format_name = serializers.CharField(source='input_format.name', read_only=True)
    output_format_name = serializers.CharField(source='output_format.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    progress_display = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FileConversion
        fields = [
            'id', 'created_at', 'completed_at', 'original_filename',
            'original_size', 'file_size_display', 'input_format_name', 
            'output_format_name', 'status', 'progress', 'progress_display',
            'error_message', 'output_filename', 'output_size', 
            'download_url', 'expires_at', 'conversion_time', 'user_username'
        ]
        read_only_fields = [
            'id', 'created_at', 'completed_at', 'status', 'progress',
            'error_message', 'output_filename', 'output_size', 
            'download_url', 'expires_at', 'conversion_time'
        ]
    
    def get_progress_display(self, obj):
        """Affichage human-readable du progrès"""
        status_labels = {
            'pending': 'En attente',
            'processing': f'En cours ({obj.progress}%)',
            'completed': 'Terminé',
            'failed': 'Échec'
        }
        return status_labels.get(obj.status, obj.status)
    
    def get_file_size_display(self, obj):
        """Affichage human-readable de la taille"""
        size = obj.original_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

class ConversionCreateSerializer(serializers.Serializer):
    """Serializer pour créer une nouvelle conversion"""
    file = serializers.FileField()
    output_format = serializers.CharField(max_length=10)
    options = serializers.JSONField(required=False, default=dict)
    
    def validate_output_format(self, value):
        """Valide que le format de sortie existe"""
        try:
            SupportedFormat.objects.get(name=value.lower(), is_output=True)
        except SupportedFormat.DoesNotExist:
            raise serializers.ValidationError("Format de sortie non supporté")
        return value.lower()
    
    def validate_file(self, value):
        """Valide le fichier uploadé"""
        # Taille max (50MB par défaut)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Fichier trop volumineux (max: {max_size // 1024 // 1024}MB)"
            )
        
        # Extension
        if not value.name:
            raise serializers.ValidationError("Nom de fichier requis")
        
        ext = value.name.split('.')[-1].lower() if '.' in value.name else ''
        if not ext:
            raise serializers.ValidationError("Extension de fichier requise")
        
        # Format supporté
        try:
            SupportedFormat.objects.get(name=ext, is_input=True)
        except SupportedFormat.DoesNotExist:
            raise serializers.ValidationError(f"Format {ext} non supporté en entrée")
        
        return value

class ConversionQuotaSerializer(serializers.ModelSerializer):
    usage_percentage = serializers.SerializerMethodField()
    remaining_conversions = serializers.SerializerMethodField()
    max_file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversionQuota
        fields = [
            'monthly_limit', 'current_month_usage', 'usage_percentage',
            'remaining_conversions', 'max_file_size', 'max_file_size_display',
            'reset_date'
        ]
    
    def get_usage_percentage(self, obj):
        """Pourcentage d'utilisation du quota"""
        if obj.monthly_limit == 0:
            return 0
        return round((obj.current_month_usage / obj.monthly_limit) * 100, 1)
    
    def get_remaining_conversions(self, obj):
        """Conversions restantes ce mois"""
        return max(0, obj.monthly_limit - obj.current_month_usage)
    
    def get_max_file_size_display(self, obj):
        """Taille max de fichier human-readable"""
        size = obj.max_file_size
        return f"{size // (1024 * 1024)} MB"