# backend/glossary/models/term_models.py
from django.db import models
from django.utils.text import slugify
from .category_models import TermCategory


class Term(models.Model):
    """Terme principal du glossaire (langue-agnostique)"""
    
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug URL")
    category = models.ForeignKey(
        TermCategory, 
        on_delete=models.CASCADE,
        related_name='terms',
        verbose_name="Catégorie"
    )
    is_essential = models.BooleanField(
        default=False, 
        help_text="Terme essentiel à connaître vs terme de niche",
        verbose_name="Essentiel"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Débutant'),
            ('intermediate', 'Intermédiaire'), 
            ('advanced', 'Avancé'),
            ('expert', 'Expert')
        ],
        default='intermediate',
        verbose_name="Niveau de difficulté"
    )
    popularity_score = models.PositiveIntegerField(
        default=0,
        help_text="Score de popularité basé sur les consultations",
        verbose_name="Score de popularité"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Terme"
        verbose_name_plural = "Termes"
        ordering = ['-popularity_score', 'slug']

    def __str__(self):
        # Prend le titre en français par défaut, ou la première traduction
        translation = self.translations.filter(language='fr').first() or self.translations.first()
        return translation.title if translation else self.slug
    
    def get_translation(self, language='fr'):
        """Récupère la traduction pour une langue donnée"""
        return self.translations.filter(language=language).first()
    
    def get_url_path(self, language='fr'):
        """Retourne l'URL complète: marketing/seo/terme-exemple"""
        return f"{self.category.get_url_path()}/{self.slug}"


class TermTranslation(models.Model):
    """Traductions des termes par langue"""
    
    LANGUAGE_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
        ('es', 'Español'),
        ('zh', '中文'),
    ]
    
    term = models.ForeignKey(
        Term, 
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name="Terme"
    )
    language = models.CharField(
        max_length=2, 
        choices=LANGUAGE_CHOICES,
        verbose_name="Langue"
    )
    context = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Contexte pour différencier (ex: 'sales' vs 'marketing')",
        verbose_name="Contexte"
    )
    
    # Contenu principal
    title = models.CharField(max_length=200, verbose_name="Titre")
    definition = models.TextField(verbose_name="Définition")
    examples = models.TextField(
        blank=True,
        help_text="Exemples concrets d'utilisation",
        verbose_name="Exemples"
    )
    
    # Contenu enrichi
    formula = models.TextField(
        blank=True,
        help_text="Formule de calcul si applicable",
        verbose_name="Formule"
    )
    benchmarks = models.TextField(
        blank=True,
        help_text="Benchmarks et données de référence", 
        verbose_name="Benchmarks"
    )
    sources = models.TextField(
        blank=True,
        help_text="Sources et références",
        verbose_name="Sources"
    )
    
    # SEO par traduction
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Traduction"
        verbose_name_plural = "Traductions"
        unique_together = ['term', 'language', 'context']
        ordering = ['language', 'context']

    def __str__(self):
        context_str = f" ({self.context})" if self.context else ""
        return f"{self.title} [{self.get_language_display()}]{context_str}"


class TermRelation(models.Model):
    """Relations entre termes (voir aussi, dépendances, etc.)"""
    
    RELATION_TYPES = [
        ('see_also', 'Voir aussi'),
        ('synonym', 'Synonyme'),
        ('antonym', 'Antonyme'),
        ('parent', 'Terme parent'),
        ('child', 'Terme enfant'),
        ('related', 'Lié'),
    ]
    
    from_term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='relations_from',
        verbose_name="Terme source"
    )
    to_term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE, 
        related_name='relations_to',
        verbose_name="Terme cible"
    )
    relation_type = models.CharField(
        max_length=20,
        choices=RELATION_TYPES,
        verbose_name="Type de relation"
    )
    weight = models.PositiveIntegerField(
        default=1,
        help_text="Poids de la relation (1-10, plus élevé = plus important)",
        verbose_name="Poids"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Relation entre termes"
        verbose_name_plural = "Relations entre termes"
        unique_together = ['from_term', 'to_term', 'relation_type']

    def __str__(self):
        return f"{self.from_term} → {self.to_term} ({self.get_relation_type_display()})"