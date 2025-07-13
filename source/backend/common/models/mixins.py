# backend/common/models/mixins.py
# /var/www/megahub/backend/common/mixins/model_mixins.py

from django.db import models
from django.utils import timezone

class TimestampedMixin(models.Model):
    """Mixin pour timestamps automatiques"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SoftDeleteMixin(models.Model):
    """Mixin pour suppression logique"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        
        # Tracking optionnel de qui a supprimé
        if user and hasattr(self, 'deleted_by'):
            self.deleted_by = user
        
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self, user=None):
        """Méthode restore manquante"""
        self.is_deleted = False
        self.deleted_at = None
        
        if user and hasattr(self, 'restored_by'):
            self.restored_by = user
        
        self.save(update_fields=['is_deleted', 'deleted_at'])

# 🆕 AJOUTER CES MIXINS
class BrandScopedMixin(models.Model):
    """Mixin pour modèles scopés par brand"""
    brand = models.ForeignKey(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set'
    )
    
    class Meta:
        abstract = True

class SlugMixin(models.Model):
    """Mixin pour modèles avec slug automatique"""
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    # Cette constante sera définie dans les modèles qui héritent
    SLUG_SOURCE_FIELD = 'name'
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.slug and hasattr(self, self.SLUG_SOURCE_FIELD):
            from django.utils.text import slugify
            source_value = getattr(self, self.SLUG_SOURCE_FIELD)
            if source_value:
                self.slug = self._generate_unique_slug(slugify(source_value))
        super().save(*args, **kwargs)
    
    def _generate_unique_slug(self, base_slug):
        """Génère un slug unique avec suffixe si nécessaire"""
        slug = base_slug
        counter = 1
        
        while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug