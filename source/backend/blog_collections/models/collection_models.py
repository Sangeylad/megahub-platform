# backend/blog_collections/models/collection_models.py

from django.db import models
from django.utils.text import slugify
from common.models.mixins import TimestampedMixin, BrandScopedMixin


class BlogCollection(TimestampedMixin, BrandScopedMixin):
    """Collections d'articles (dossiers, séries, formations)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    COLLECTION_TYPES = [
        ('dossier', 'Dossier Thématique'),
        ('serie', 'Série d\'Articles'),
        ('formation', 'Formation'),
        ('guide', 'Guide Complet'),
        ('newsletter', 'Série Newsletter'),
    ]
    collection_type = models.CharField(
        max_length=20,
        choices=COLLECTION_TYPES,
        default='dossier'
    )
    
    # Template et apparence
    template_page = models.ForeignKey(
        'seo_pages_content.Page',  # ← FIX: Au lieu de 'seo_analyzer.Page'
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_collections',
        help_text="Template pour cette collection"
    )
    
    cover_image_url = models.URLField(
        blank=True,
        help_text="Image de couverture de la collection"
    )
    
    # Relations articles
    articles = models.ManyToManyField(
        'blog_content.BlogArticle',
        through='BlogCollectionItem',
        related_name='collections'
    )
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=False,
        help_text="Collection mise en avant"
    )
    is_sequential = models.BooleanField(
        default=True,
        help_text="Lecture séquentielle recommandée"
    )
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Créateur
    created_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='created_collections'
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while BlogCollection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_articles_ordered(self):
        """Articles de la collection dans l'ordre"""
        return self.articles.filter(
            blogcollectionitem__collection=self
        ).order_by('blogcollectionitem__order').select_related('page', 'primary_author')
    
    def get_articles_count(self):
        """Nombre d'articles dans la collection"""
        return self.articles.count()
    
    def get_published_articles_count(self):
        """Nombre d'articles publiés dans la collection"""
        return self.articles.filter(page__status='published').count()
    
    def get_reading_time_total(self):
        """Temps de lecture total estimé"""
        total_time = 0
        for article in self.articles.all():
            total_time += article.reading_time_minutes
        return total_time
    
    def __str__(self):
        return f"{self.name} ({self.get_collection_type_display()})"
    
    class Meta:
        verbose_name = "Collection Blog"
        verbose_name_plural = "Collections Blog"
        db_table = 'blog_collections_blogcollection'
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['collection_type', 'is_active']),
            models.Index(fields=['is_featured', 'created_at']),
        ]


class BlogCollectionItem(TimestampedMixin):
    """Articles dans une collection avec ordre et métadonnées"""
    collection = models.ForeignKey(
        BlogCollection, 
        on_delete=models.CASCADE,
        related_name='collection_items'
    )
    article = models.ForeignKey(
        'blog_content.BlogArticle', 
        on_delete=models.CASCADE,
        related_name='collection_items'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordre dans la collection"
    )
    
    # Métadonnées spécifiques à la collection
    custom_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Titre personnalisé dans cette collection"
    )
    custom_description = models.TextField(
        blank=True,
        help_text="Description personnalisée"
    )
    
    # Configuration
    is_optional = models.BooleanField(
        default=False,
        help_text="Article optionnel dans le parcours"
    )
    is_bonus = models.BooleanField(
        default=False,
        help_text="Contenu bonus"
    )
    
    # Ajouté par
    added_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='added_collection_items'
    )
    
    def get_display_title(self):
        """Titre à afficher (custom ou original)"""
        return self.custom_title or self.article.page.title
    
    def get_display_description(self):
        """Description à afficher"""
        return self.custom_description or self.article.get_auto_excerpt()
    
    def get_next_item(self):
        """Article suivant dans la collection"""
        return BlogCollectionItem.objects.filter(
            collection=self.collection,
            order__gt=self.order
        ).order_by('order').first()
    
    def get_previous_item(self):
        """Article précédent dans la collection"""
        return BlogCollectionItem.objects.filter(
            collection=self.collection,
            order__lt=self.order
        ).order_by('-order').first()
    
    def __str__(self):
        return f"{self.collection.name} - {self.get_display_title()} (#{self.order})"
    
    class Meta:
        unique_together = ['collection', 'article']
        ordering = ['order']
        verbose_name = "Article Collection"
        verbose_name_plural = "Articles Collection"
        db_table = 'blog_collections_blogcollectionitem'
        indexes = [
            models.Index(fields=['collection', 'order']),
        ]