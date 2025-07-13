# backend/public_tools/models.py
from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone

class ToolUsage(models.Model):
    """Tracking simple de l'usage des outils"""
    tool_name = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'public_tools_usage'
    
    def __str__(self):
        return f"{self.tool_name} - {self.created_at}"

class PublicFileConversion(models.Model):
    """Conversions publiques sans user/brand"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    # Tracking
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Fichier
    original_filename = models.CharField(max_length=255)
    original_size = models.PositiveIntegerField()
    input_format = models.CharField(max_length=10)  # Pas de FK pour simplifier
    output_format = models.CharField(max_length=10)
    
    # État
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Résultat
    output_filename = models.CharField(max_length=255, blank=True)
    output_size = models.PositiveIntegerField(null=True, blank=True)
    download_token = models.UUIDField(default=uuid.uuid4, unique=True)
    conversion_time = models.FloatField(null=True, blank=True)
    
    # Auto-expiration agressive (1h)
    expires_at = models.DateTimeField()
    
    # Tâche
    task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'public_tools_file_conversion'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['download_token']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Public: {self.original_filename} ({self.status})"

class PublicConversionQuota(models.Model):
    """Quotas par IP pour éviter les abus"""
    ip_address = models.GenericIPAddressField(unique=True)
    hourly_usage = models.PositiveIntegerField(default=0)
    daily_usage = models.PositiveIntegerField(default=0)
    last_conversion = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, blank=True)
    
    # Limites strictes
    HOURLY_LIMIT = 10
    DAILY_LIMIT = 50
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    class Meta:
        db_table = 'public_tools_conversion_quota'
    
    def can_convert(self, file_size=0):
        """Vérifie si la conversion est autorisée"""
        if self.is_blocked:
            return False, f"IP bloquée: {self.block_reason}"
        
        if file_size > self.MAX_FILE_SIZE:
            return False, f"Fichier trop volumineux (max: {self.MAX_FILE_SIZE // 1024 // 1024}MB)"
        
        # Reset quotas si nécessaire
        now = timezone.now()
        if self.last_conversion.date() < now.date():
            self.daily_usage = 0
        if self.last_conversion.hour < now.hour or self.last_conversion.date() < now.date():
            self.hourly_usage = 0
        
        if self.hourly_usage >= self.HOURLY_LIMIT:
            return False, f"Limite horaire atteinte ({self.HOURLY_LIMIT}/h)"
        
        if self.daily_usage >= self.DAILY_LIMIT:
            return False, f"Limite quotidienne atteinte ({self.DAILY_LIMIT}/jour)"
        
        return True, ""
    
    def increment_usage(self):
        """Incrémente les compteurs"""
        self.hourly_usage += 1
        self.daily_usage += 1
        self.save()
        
class PublicFileCompression(models.Model):
    """Compressions publiques sans user/brand"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    COMPRESSION_LEVEL_CHOICES = [
        ('fastest', 'Rapide'),
        ('normal', 'Normal'),
        ('maximum', 'Maximum'),
    ]
    
    # Tracking
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Fichiers sources
    source_files_info = models.JSONField(default=list)  # [{"name": "file.txt", "size": 1024}]
    total_source_size = models.PositiveBigIntegerField()
    files_count = models.PositiveIntegerField()
    
    # Configuration
    output_format = models.CharField(max_length=10, default='zip')  # Simplifié pour public
    compression_level = models.CharField(max_length=20, choices=COMPRESSION_LEVEL_CHOICES, default='normal')
    
    # État
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Résultat
    archive_filename = models.CharField(max_length=255, blank=True)
    archive_size = models.PositiveBigIntegerField(null=True, blank=True)
    compression_ratio = models.FloatField(null=True, blank=True)
    download_token = models.UUIDField(default=uuid.uuid4, unique=True)
    compression_time = models.FloatField(null=True, blank=True)
    
    # Auto-expiration très agressive (30 minutes)
    expires_at = models.DateTimeField()
    
    # Tâche
    task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'public_tools_file_compression'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['download_token']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 30 minutes seulement pour les compressions publiques
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def formatted_ratio(self):
        if self.compression_ratio:
            return f"{(1 - self.compression_ratio) * 100:.1f}%"
        return "N/A"
    
    def __str__(self):
        return f"Public: {self.archive_filename} ({self.files_count} fichiers)"

class PublicCompressionQuota(models.Model):
    """Quotas très restrictifs pour compressions publiques"""
    ip_address = models.GenericIPAddressField(unique=True)
    hourly_usage = models.PositiveIntegerField(default=0)
    daily_usage = models.PositiveIntegerField(default=0)
    last_compression = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, blank=True)
    
    # Limites très strictes pour compressions
    HOURLY_LIMIT = 3
    DAILY_LIMIT = 10
    MAX_TOTAL_SIZE = 25 * 1024 * 1024  # 25MB total
    MAX_FILES_COUNT = 20  # Max 20 fichiers
    MAX_SINGLE_FILE = 10 * 1024 * 1024  # 10MB par fichier
    
    class Meta:
        db_table = 'public_tools_compression_quota'
    
    def can_compress(self, files_count=0, total_size=0, max_single_size=0):
        """Vérifie si la compression est autorisée"""
        if self.is_blocked:
            return False, f"IP bloquée: {self.block_reason}"
        
        if total_size > self.MAX_TOTAL_SIZE:
            return False, f"Taille totale trop importante (max: {self.MAX_TOTAL_SIZE // 1024 // 1024}MB)"
        
        if files_count > self.MAX_FILES_COUNT:
            return False, f"Trop de fichiers (max: {self.MAX_FILES_COUNT})"
        
        if max_single_size > self.MAX_SINGLE_FILE:
            return False, f"Fichier individuel trop gros (max: {self.MAX_SINGLE_FILE // 1024 // 1024}MB)"
        
        # Reset quotas si nécessaire
        now = timezone.now()
        if self.last_compression.date() < now.date():
            self.daily_usage = 0
        if self.last_compression.hour < now.hour or self.last_compression.date() < now.date():
            self.hourly_usage = 0
        
        if self.hourly_usage >= self.HOURLY_LIMIT:
            return False, f"Limite horaire atteinte ({self.HOURLY_LIMIT}/h)"
        
        if self.daily_usage >= self.DAILY_LIMIT:
            return False, f"Limite quotidienne atteinte ({self.DAILY_LIMIT}/jour)"
        
        return True, ""
    
    def increment_usage(self):
        """Incrémente les compteurs"""
        self.hourly_usage += 1
        self.daily_usage += 1
        self.save()
        
# Ajouter à la fin du fichier existant

class PublicFileOptimization(models.Model):
    """Optimisations publiques sans user/brand"""
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
    ]
    
    # Tracking
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Fichier source
    original_filename = models.CharField(max_length=255)
    original_size = models.PositiveBigIntegerField()
    original_mime_type = models.CharField(max_length=100)
    file_extension = models.CharField(max_length=10)
    
    # Configuration simple pour public
    quality_level = models.CharField(max_length=20, choices=QUALITY_LEVEL_CHOICES, default='medium')
    resize_enabled = models.BooleanField(default=False)
    target_max_dimension = models.PositiveIntegerField(null=True, blank=True)
    
    # État
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Résultat
    optimized_filename = models.CharField(max_length=255, blank=True)
    optimized_size = models.PositiveBigIntegerField(null=True, blank=True)
    compression_ratio = models.FloatField(null=True, blank=True)
    size_reduction_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    size_reduction_percentage = models.FloatField(null=True, blank=True)
    download_token = models.UUIDField(default=uuid.uuid4, unique=True)
    optimization_time = models.FloatField(null=True, blank=True)
    
    # Auto-expiration agressive (1 heure)
    expires_at = models.DateTimeField()
    
    # Tâche
    task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'public_tools_file_optimization'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['download_token']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 1 heure seulement pour les optimisations publiques
            self.expires_at = timezone.now() + timedelta(hours=1)
        
        # Calcul automatique des métriques
        if self.original_size and self.optimized_size:
            self.compression_ratio = self.optimized_size / self.original_size
            self.size_reduction_bytes = self.original_size - self.optimized_size
            self.size_reduction_percentage = (1 - self.compression_ratio) * 100
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def formatted_reduction(self):
        if self.size_reduction_percentage:
            return f"{self.size_reduction_percentage:.1f}%"
        return "N/A"
    
    def __str__(self):
        return f"Public: {self.original_filename} -> {self.optimized_filename or 'En cours'}"

class PublicOptimizationQuota(models.Model):
    """Quotas très restrictifs pour optimisations publiques"""
    ip_address = models.GenericIPAddressField(unique=True)
    hourly_usage = models.PositiveIntegerField(default=0)
    daily_usage = models.PositiveIntegerField(default=0)
    last_optimization = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, blank=True)
    
    # Limites très strictes pour optimisations publiques
    HOURLY_LIMIT = 5
    DAILY_LIMIT = 20
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DIMENSION = 2048  # Résolution max
    
    class Meta:
        db_table = 'public_tools_optimization_quota'
    
    def can_optimize(self, file_size=0):
        """Vérifie si l'optimisation est autorisée"""
        if self.is_blocked:
            return False, f"IP bloquée: {self.block_reason}"
        
        if file_size > self.MAX_FILE_SIZE:
            return False, f"Fichier trop volumineux (max: {self.MAX_FILE_SIZE // 1024 // 1024}MB)"
        
        # Reset quotas si nécessaire
        now = timezone.now()
        if self.last_optimization.date() < now.date():
            self.daily_usage = 0
        if self.last_optimization.hour < now.hour or self.last_optimization.date() < now.date():
            self.hourly_usage = 0
        
        if self.hourly_usage >= self.HOURLY_LIMIT:
            return False, f"Limite horaire atteinte ({self.HOURLY_LIMIT}/h)"
        
        if self.daily_usage >= self.DAILY_LIMIT:
            return False, f"Limite quotidienne atteinte ({self.DAILY_LIMIT}/jour)"
        
        return True, ""
    
    def increment_usage(self):
        """Incrémente les compteurs"""
        self.hourly_usage += 1
        self.daily_usage += 1
        self.save()