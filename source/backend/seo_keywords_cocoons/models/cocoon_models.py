# backend/seo_keywords_cocoons/models/cocoon_models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.core.exceptions import ValidationError

# Common - avec fallback
try:
    from common.models.mixins import TimestampedMixin, SlugMixin
except ImportError:
    class TimestampedMixin(models.Model):
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        class Meta:
            abstract = True
    
    class SlugMixin(models.Model):
        SLUG_SOURCE_FIELD = 'name'
        class Meta:
            abstract = True

class CocoonCategory(TimestampedMixin):
    """Catégories thématiques de cocons"""
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(
        max_length=7, 
        default='#3498db',
        help_text="Couleur hexadécimale pour l'interface"
    )
    
    def clean(self):
        """Validation couleur hexadécimale"""
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError({
                'color': 'La couleur doit être au format hexadécimal (#RRGGBB)'
            })
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'seo_keywords_cocoons_cocooncategory'
        ordering = ['name']

class SemanticCocoon(TimestampedMixin, SlugMixin):
    """Cocons sémantiques - pools de mots-clés thématiques"""
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    
    categories = models.ManyToManyField(
        CocoonCategory, 
        related_name='cocoons', 
        blank=True
    )
    
    # Intégration OpenAI
    openai_file_id = models.CharField(max_length=255, blank=True, null=True)
    openai_vector_store_id = models.CharField(max_length=255, blank=True, null=True)
    openai_storage_type = models.CharField(
        max_length=20,
        choices=[('file', 'File'), ('vector_store', 'Vector Store')],
        default='vector_store'
    )
    openai_file_version = models.IntegerField(default=0)
    last_pushed_at = models.DateTimeField(null=True, blank=True)
    
    # SlugMixin configuration
    SLUG_SOURCE_FIELD = 'name'
    
    def __str__(self):
        return self.name
    
    def needs_sync(self):
        """Vérifie si le cocon nécessite une synchronisation OpenAI"""
        if not self.last_pushed_at:
            return True
        return self.updated_at > self.last_pushed_at
    
    class Meta:
        db_table = 'seo_keywords_cocoons_semanticcocoon'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]