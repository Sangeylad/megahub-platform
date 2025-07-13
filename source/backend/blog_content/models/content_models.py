# backend/blog_content/models/content_models.py

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from common.models.mixins import TimestampedMixin, BrandScopedMixin
from django.utils.text import slugify


class BlogAuthor(TimestampedMixin):
    """Auteur blog - version allégée pour contenu pur"""
    user = models.OneToOneField(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='blog_author'
    )
    
    # Infos publiques auteur
    display_name = models.CharField(
        max_length=100,
        help_text="Nom affiché publiquement"
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="Biographie courte"
    )
    avatar_url = models.URLField(blank=True)
    
    # Links sociaux
    website_url = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Métadonnées éditoriales
    expertise_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="Sujets d'expertise ['SEO', 'Content Marketing']"
    )
    
    # Stats basiques
    articles_count = models.PositiveIntegerField(default=0)
    
    def get_full_name(self):
        return self.display_name or self.user.get_full_name() or self.user.username
    
    def update_articles_count(self):
        """Met à jour le compteur d'articles"""
        self.articles_count = self.blog_articles.filter(
            publishing_status__status='published'  # ✅ Via la relation publishing_status
        ).count()
        self.save(update_fields=['articles_count'])
    
    def __str__(self):
        return self.get_full_name()
    
    class Meta:
        verbose_name = "Auteur Blog"
        verbose_name_plural = "Auteurs Blog"
        db_table = 'blog_content_blogauthor'


class BlogTag(TimestampedMixin):
    """Tags pour articles - version core"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text="Couleur hexadécimale"
    )
    
    # SEO basique
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Stats
    usage_count = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def update_usage_count(self):
        self.usage_count = self.blog_articles.filter(
            page__status='published'
        ).count()
        self.save(update_fields=['usage_count'])
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Tag Blog"
        verbose_name_plural = "Tags Blog"
        db_table = 'blog_content_blogtag'


class BlogArticle(TimestampedMixin):
    """Article blog - version core sans logique complexe"""
    page = models.OneToOneField(
        'seo_pages_content.Page',  # ✅ NOUVEAU - pointer vers la bonne app !
        on_delete=models.CASCADE,
        related_name='blog_article'
    )
    
    # Relations éditoriales
    primary_author = models.ForeignKey(
        BlogAuthor,
        on_delete=models.PROTECT,
        related_name='blog_articles'
    )
    co_authors = models.ManyToManyField(
        BlogAuthor,
        blank=True,
        related_name='co_authored_articles'
    )
    
    # Contenu de base
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text="Résumé article"
    )
    
    # Médias
    featured_image_url = models.URLField(blank=True)
    featured_image_alt = models.CharField(max_length=200, blank=True)
    featured_image_caption = models.CharField(max_length=300, blank=True)
    
    # Classification
    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        related_name='blog_articles'
    )
    
    # SEO basique
    focus_keyword = models.CharField(max_length=100, blank=True)
    
    # Métadonnées calculées (gérées par blog_editor)
    word_count = models.PositiveIntegerField(default=0)
    reading_time_minutes = models.PositiveIntegerField(default=5)
    
    def get_full_url_path(self):
        return self.page.url_path
    
    def get_category(self):
        return self.page.parent if self.page.parent else None
    
    def get_auto_excerpt(self):
        if self.excerpt:
            return self.excerpt
        # Logique basique - blog_editor aura la vraie logique
        return f"Article par {self.primary_author.get_full_name()}"
    
    def __str__(self):
        return f"{self.page.title} by {self.primary_author.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Article Blog"
        verbose_name_plural = "Articles Blog"
        db_table = 'blog_content_blogarticle'
        indexes = [
            models.Index(fields=['primary_author', 'created_at']),
        ]