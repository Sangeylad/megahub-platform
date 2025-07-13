# backend/file_compressor/models.py
from django.db import models
from django.contrib.auth import get_user_model
from brands_core.models import Brand
import uuid
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class SupportedFileType(models.Model):
    """Types de fichiers supportés pour la compression"""
    name = models.CharField(max_length=50, unique=True)  # 'pdf', 'jpeg', 'png', 'webp'
    extension = models.CharField(max_length=10)  # '.pdf', '.jpg', etc.
    mime_type = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=[
        ('document', 'Document'),
        ('image', 'Image'), 
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
    ])
    average_compression_ratio = models.FloatField(default=0.5)  # Ratio moyen de compression
    is_active = models.BooleanField(default=True)
    max_file_size = models.PositiveIntegerField(default=50 * 1024 * 1024)  # 50MB par défaut
    
    # Paramètres de compression spécifiques
    supports_quality_levels = models.BooleanField(default=True)
    supports_resize = models.BooleanField(default=False)
    default_quality = models.PositiveSmallIntegerField(default=75)  # 0-100
    
    class Meta:
        db_table = 'file_compressor_supported_type'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class FileOptimization(models.Model):
    """Historique des optimisations de fichiers"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    QUALITY_LEVEL_CHOICES = [
        ('low', 'Basse qualité (compression max)'),
        ('medium', 'Qualité moyenne'),
        ('high', 'Haute qualité (compression légère)'),
        ('lossless', 'Sans perte (si supporté)'),
    ]
    
    # Métadonnées
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Fichier source
    original_filename = models.CharField(max_length=255)
    original_size = models.PositiveBigIntegerField()  # bytes
    original_mime_type = models.CharField(max_length=100)
    file_type = models.ForeignKey(SupportedFileType, on_delete=models.CASCADE)
    
    # Configuration d'optimisation
    quality_level = models.CharField(max_length=20, choices=QUALITY_LEVEL_CHOICES, default='medium')
    custom_quality = models.PositiveSmallIntegerField(null=True, blank=True)  # 0-100 si custom
    resize_enabled = models.BooleanField(default=False)
    target_width = models.PositiveIntegerField(null=True, blank=True)
    target_height = models.PositiveIntegerField(null=True, blank=True)
    maintain_aspect_ratio = models.BooleanField(default=True)
    
    # État
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.PositiveSmallIntegerField(default=0)  # 0-100
    error_message = models.TextField(blank=True)
    
    # Résultat
    optimized_filename = models.CharField(max_length=255, blank=True)
    optimized_size = models.PositiveBigIntegerField(null=True, blank=True)
    compression_ratio = models.FloatField(null=True, blank=True)  # optimized_size / original_size
    size_reduction_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    size_reduction_percentage = models.FloatField(null=True, blank=True)
    download_url = models.URLField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées techniques
    optimization_time = models.FloatField(null=True, blank=True)  # secondes
    task_id = models.CharField(max_length=255, blank=True)
    
    # Métadonnées fichier optimisé (si applicable)
    final_dimensions = models.JSONField(null=True, blank=True)  # {"width": 1920, "height": 1080}
    final_quality = models.PositiveSmallIntegerField(null=True, blank=True)
    optimization_details = models.JSONField(null=True, blank=True)  # Détails techniques
    
    class Meta:
        db_table = 'file_compressor_optimization'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'brand', '-created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['file_type', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expires_at and self.status == 'completed':
            # 7 jours pour les optimisations privées
            self.expires_at = timezone.now() + timedelta(days=7)
        
        # Calcul automatique des métriques
        if self.original_size and self.optimized_size:
            self.compression_ratio = self.optimized_size / self.original_size
            self.size_reduction_bytes = self.original_size - self.optimized_size
            self.size_reduction_percentage = (1 - self.compression_ratio) * 100
        
        super().save(*args, **kwargs)
    
    @property
    def formatted_reduction(self):
        if self.size_reduction_percentage:
            return f"{self.size_reduction_percentage:.1f}%"
        return "N/A"
    
    @property
    def size_reduction_mb(self):
        if self.size_reduction_bytes:
            return self.size_reduction_bytes / (1024 * 1024)
        return 0
    
    def __str__(self):
        return f"{self.original_filename} -> {self.optimized_filename or 'En cours'}"

class OptimizationQuota(models.Model):
    """Quotas d'optimisation par brand"""
    brand = models.OneToOneField(Brand, on_delete=models.CASCADE)
    monthly_limit = models.PositiveIntegerField(default=100)  # 100 fichiers/mois
    current_month_usage = models.PositiveIntegerField(default=0)
    max_file_size = models.PositiveBigIntegerField(default=50 * 1024 * 1024)  # 50MB
    reset_date = models.DateTimeField()
    
    # Fonctionnalités premium
    can_use_lossless = models.BooleanField(default=False)
    can_resize = models.BooleanField(default=True)
    can_custom_quality = models.BooleanField(default=True)
    max_resolution = models.PositiveIntegerField(default=1920)  # Largeur max
    
    class Meta:
        db_table = 'file_compressor_quota'
    
    def can_optimize(self, file_size=0):
        """Vérifie si l'optimisation est autorisée"""
        if self.current_month_usage >= self.monthly_limit:
            return False, "Quota mensuel d'optimisations dépassé"
        
        if file_size > self.max_file_size:
            max_mb = self.max_file_size // 1024 // 1024
            return False, f"Fichier trop volumineux (max: {max_mb}MB)"
        
        return True, ""
    
    def increment_usage(self):
        """Incrémente l'usage mensuel"""
        self.current_month_usage += 1
        self.save(update_fields=['current_month_usage'])