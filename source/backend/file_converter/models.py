# backend/file_converter/models.py
from django.db import models
from django.contrib.auth import get_user_model
from brands_core.models import Brand

User = get_user_model()

class SupportedFormat(models.Model):
    """Formats supportés pour la conversion"""
    name = models.CharField(max_length=50, unique=True)  # 'pdf', 'docx', 'md', etc.
    mime_type = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=[
        ('document', 'Document'),
        ('image', 'Image'), 
        ('presentation', 'Présentation'),
        ('spreadsheet', 'Tableur'),
    ])
    is_input = models.BooleanField(default=True)  # Peut être source
    is_output = models.BooleanField(default=True)  # Peut être cible
    
    class Meta:
        db_table = 'file_converter_supported_format'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class FileConversion(models.Model):
    """Historique des conversions"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    # Métadonnées
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Fichiers
    original_filename = models.CharField(max_length=255)
    original_size = models.PositiveIntegerField()  # bytes
    input_format = models.ForeignKey(
        SupportedFormat, 
        on_delete=models.CASCADE, 
        related_name='input_conversions'
    )
    output_format = models.ForeignKey(
        SupportedFormat, 
        on_delete=models.CASCADE, 
        related_name='output_conversions'
    )
    
    # État
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.PositiveSmallIntegerField(default=0)  # 0-100
    error_message = models.TextField(blank=True)
    
    # Résultat
    output_filename = models.CharField(max_length=255, blank=True)
    output_size = models.PositiveIntegerField(null=True, blank=True)
    download_url = models.URLField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Auto-cleanup
    
    # Métadonnées techniques
    conversion_time = models.FloatField(null=True, blank=True)  # secondes
    task_id = models.CharField(max_length=255, blank=True)  # Celery task ID
    
    class Meta:
        db_table = 'file_converter_conversion'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'brand', '-created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} → {self.output_format.name}"

class ConversionQuota(models.Model):
    """Quotas de conversion par brand"""
    brand = models.OneToOneField(Brand, on_delete=models.CASCADE)
    monthly_limit = models.PositiveIntegerField(default=100)
    current_month_usage = models.PositiveIntegerField(default=0)
    max_file_size = models.PositiveIntegerField(default=50 * 1024 * 1024)  # 50MB
    reset_date = models.DateTimeField()  # Prochaine remise à zéro
    
    class Meta:
        db_table = 'file_converter_quota'
    
    def can_convert(self, file_size=0):
        """Vérifie si la conversion est autorisée"""
        if self.current_month_usage >= self.monthly_limit:
            return False, "Quota mensuel dépassé"
        if file_size > self.max_file_size:
            return False, f"Fichier trop volumineux (max: {self.max_file_size // 1024 // 1024}MB)"
        return True, ""
    
    def increment_usage(self):
        """Incrémente l'usage mensuel"""
        self.current_month_usage += 1
        self.save(update_fields=['current_month_usage'])