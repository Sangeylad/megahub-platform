# backend/glossary/models/category_models.py
from django.db import models
from django.utils.text import slugify


class TermCategory(models.Model):
    """Catégories hiérarchiques pour organiser les termes du glossaire"""
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug URL")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name="Catégorie parente"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    color = models.CharField(
        max_length=7, 
        default="#6a5acd", 
        help_text="Couleur hexadécimale pour l'UI",
        verbose_name="Couleur"
    )
    icon = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Classe CSS d'icône (ex: fas fa-bullhorn)",
        verbose_name="Icône"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.get_full_path()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """Retourne le chemin complet: Marketing > SEO > Technique"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_url_path(self):
        """Retourne le chemin URL: marketing/seo/technique"""
        if self.parent:
            return f"{self.parent.get_url_path()}/{self.slug}"
        return self.slug
    
    def get_level(self):
        """Retourne le niveau hiérarchique (0 = racine)"""
        if self.parent:
            return self.parent.get_level() + 1
        return 0
    
    @property
    def terms_count(self):
        """Nombre de termes dans cette catégorie (inclut sous-catégories)"""
        from .term_models import Term
        category_ids = [self.id] + list(self.get_descendants().values_list('id', flat=True))
        return Term.objects.filter(category_id__in=category_ids, is_active=True).count()
    
    def get_descendants(self):
        """Retourne tous les descendants (récursif)"""
        descendants = TermCategory.objects.filter(parent=self)
        for child in descendants:
            descendants = descendants.union(child.get_descendants())
        return descendants
    
    def get_ancestors(self):
        """Retourne tous les ancêtres jusqu'à la racine"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return reversed(ancestors)