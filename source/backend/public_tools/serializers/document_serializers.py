# backend/public_tools/serializers/document_serializers.py
from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from ..models import PublicFileConversion

class ConversionRequestSerializer(serializers.Serializer):
    """Validation des demandes de conversion publiques"""
    file = serializers.FileField()
    target_format = serializers.CharField(max_length=10)
    
    def validate_file(self, value: UploadedFile):
        """Validation stricte du fichier"""
        # Taille max 10MB
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f"Fichier trop volumineux (max: 10MB)")
        
        # Extensions autorisées
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.html']
        file_ext = '.' + value.name.split('.')[-1].lower() if '.' in value.name else ''
        
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(f"Format non autorisé. Formats acceptés: {', '.join(allowed_extensions)}")
        
        return value
    
    def validate_target_format(self, value):
        """Validation du format cible"""
        allowed_formats = ['pdf', 'docx', 'txt', 'md', 'html']
        value = value.lower().strip()
        
        if value not in allowed_formats:
            raise serializers.ValidationError(f"Format cible non autorisé. Formats disponibles: {', '.join(allowed_formats)}")
        
        return value

class BatchConversionRequestSerializer(serializers.Serializer):
    """Validation pour conversions multiples"""
    files = serializers.ListField(
        child=serializers.FileField(),
        max_length=10,  # Max 10 fichiers
        min_length=1,
        error_messages={
            'max_length': 'Maximum 10 fichiers autorisés',
            'min_length': 'Au moins un fichier requis'
        }
    )
    target_format = serializers.CharField(max_length=10)
    
    def validate_files(self, files):
        """Validation de chaque fichier"""
        single_serializer = ConversionRequestSerializer()
        
        for file in files:
            # Réutiliser la validation du fichier unique
            single_serializer.validate_file(file)
        
        return files
    
    def validate_target_format(self, value):
        """Validation du format cible"""
        single_serializer = ConversionRequestSerializer()
        return single_serializer.validate_target_format(value)

class PublicConversionStatusSerializer(serializers.ModelSerializer):
    """Sérializer pour le statut de conversion publique"""
    progress_percentage = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PublicFileConversion
        fields = [
            'id', 'status', 'original_filename', 'output_format',
            'created_at', 'completed_at', 'conversion_time',
            'progress_percentage', 'time_remaining', 'download_url',
            'error_message', 'original_size', 'output_size'
        ]
        read_only_fields = [
            'id', 'status', 'original_filename', 'output_format',
            'created_at', 'completed_at', 'conversion_time',
            'error_message', 'original_size', 'output_size'
        ]
    
    def get_progress_percentage(self, obj):
        """Calcule le pourcentage de progression"""
        if obj.status == 'pending':
            return 0
        elif obj.status == 'processing':
            return 50  # Estimation simple
        elif obj.status in ['completed', 'failed']:
            return 100
        return 0
    
    def get_time_remaining(self, obj):
        """Estimation du temps restant"""
        if obj.status == 'pending':
            return "En attente..."
        elif obj.status == 'processing':
            return "Quelques secondes..."
        elif obj.status == 'completed':
            return "Terminé"
        elif obj.status == 'failed':
            return "Échec"
        return "Inconnu"
    
    def get_download_url(self, obj):
        """URL de téléchargement si disponible"""
        if obj.status == 'completed' and not obj.is_expired:
            return f"/wp-admin/admin-ajax.php?action=humari_download_file&token={obj.download_token}"
        return None