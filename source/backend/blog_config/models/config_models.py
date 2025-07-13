# backend/blog_config/models/config_models.py
from django.db import models
from common.models.mixins import TimestampedMixin

class BlogConfig(TimestampedMixin):
    """Configuration globale du blog par website"""
    website = models.OneToOneField(
        'seo_websites_core.Website',  # ← FIX: Nouvelle référence
        on_delete=models.CASCADE, 
        related_name='blog_config'
    )
    
    # Identité du blog
    blog_name = models.CharField(
        max_length=100,
        help_text="Nom affiché du blog"
    )
    blog_slug = models.SlugField(
        max_length=50,
        help_text="Slug URL du blog"
    )
    blog_description = models.TextField(
        blank=True,
        help_text="Description pour SEO"
    )
    
    # Templates de référence
    template_article_page = models.ForeignKey(
        'seo_pages_content.Page',  # ← FIX: Nouvelle référence
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_article_templates',
        help_text="Page template pour articles"
    )
    template_category_page = models.ForeignKey(
        'seo_pages_content.Page',  # ← FIX: Nouvelle référence
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_category_templates',
        help_text="Page template pour catégories"
    )
    template_archive_page = models.ForeignKey(
        'seo_pages_content.Page',  # ← FIX: Nouvelle référence
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_archive_templates',
        help_text="Page template pour archives"
    )
    
    # Configuration affichage
    posts_per_page = models.PositiveIntegerField(
        default=12,
        help_text="Articles par page"
    )
    posts_per_rss = models.PositiveIntegerField(
        default=20,
        help_text="Articles dans flux RSS"
    )
    excerpt_length = models.PositiveIntegerField(
        default=160,
        help_text="Longueur auto des extraits"
    )
    
    # Fonctionnalités
    enable_comments = models.BooleanField(default=False)
    enable_newsletter = models.BooleanField(default=True)
    enable_related_posts = models.BooleanField(default=True)
    enable_auto_publish = models.BooleanField(
        default=False,
        help_text="Publication automatique des articles programmés"
    )
    
    # SEO patterns
    default_meta_title_pattern = models.CharField(
        max_length=200,
        default="{{article.title}} | {{blog.name}}",
        help_text="Pattern titre SEO"
    )
    default_meta_description_pattern = models.CharField(
        max_length=300,
        default="{{article.excerpt|truncate:150}}",
        help_text="Pattern description SEO"
    )
    
    # Analytics
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="GA ID spécifique blog"
    )
    
    # Configuration éditeur
    default_featured_image = models.URLField(
        blank=True,
        help_text="Image par défaut pour articles"
    )
    auto_generate_excerpts = models.BooleanField(
        default=True,
        help_text="Générer automatiquement les extraits"
    )
    
    def get_blog_base_url(self):
        """URL de base du blog"""
        return f"/{self.blog_slug}/"
    
    def get_full_blog_url(self):
        """URL complète du blog"""
        return f"{self.website.url.rstrip('/')}/{self.blog_slug}/"
    
    def get_total_articles(self):
        """Nombre total d'articles pour ce blog"""
        from blog_content.models import BlogArticle
        return BlogArticle.objects.filter(page__website=self.website).count()
    
    def get_published_articles(self):
        """Nombre d'articles publiés"""
        from blog_content.models import BlogArticle
        return BlogArticle.objects.filter(
            page__website=self.website,
            page__status='published'
        ).count()
    
    def __str__(self):
        return f"{self.blog_name} ({self.website.name})"
    
    class Meta:
        verbose_name = "Configuration Blog"
        verbose_name_plural = "Configurations Blog"
        db_table = 'blog_config_blogconfig'