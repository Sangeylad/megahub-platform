# backend/seo_websites_core/serializers/website_serializers.py

from rest_framework import serializers
from django.db.models import Count

from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin  # ← FIX: Bon chemin
from .base_serializers import WebsiteCoreBaseSerializer
from ..models import Website

class WebsiteListSerializer(StatsMixin, DynamicFieldsSerializer, WebsiteCoreBaseSerializer):
    """
    🔥 SERIALIZER CONDITIONNEL : Champs selon filtres appliqués
    
    Logique intelligente :
    - Champs de base : TOUJOURS (id, name, url, brand_name, etc.)
    - Champs conditionnels : Ajoutés SI annotations présentes dans queryset
    - Stats calculées : Via StatsMixin si contexte approprié
    """
    
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    pages_count = serializers.SerializerMethodField()
    
    # 🔥 Champs conditionnels (ajoutés si annotations présentes)
    total_keywords = serializers.IntegerField(read_only=True)
    unique_keywords = serializers.IntegerField(read_only=True)
    avg_sitemap_priority = serializers.FloatField(read_only=True)
    published_pages = serializers.IntegerField(read_only=True)
    draft_pages = serializers.IntegerField(read_only=True)
    total_sections = serializers.IntegerField(read_only=True)
    pages_with_layout = serializers.IntegerField(read_only=True)
    excluded_pages = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Website
        fields = [
            'id', 'name', 'url', 'brand_name', 'domain_authority',
            'max_competitor_backlinks', 'max_competitor_kd',
            'pages_count', 'created_at', 'updated_at'
        ]
        
        # 🔥 Configuration champs conditionnels via StatsMixin
        stats_fields = {
            'keywords_ratio': 'get_keywords_ratio',
            'publication_ratio': 'get_publication_ratio', 
            'layout_coverage': 'get_layout_coverage',
            'seo_coverage': 'get_seo_coverage',
            'performance_score': 'get_performance_score'
        }
    
    def __init__(self, *args, **kwargs):
        """🔥 INITIALISATION INTELLIGENTE : Ajout dynamique selon annotations"""
        super().__init__(*args, **kwargs)
        
        # Détection instance(s) pour analyser annotations disponibles
        instance = kwargs.get('instance')
        if instance and hasattr(instance, '__iter__'):
            # C'est une liste/queryset
            first_obj = next(iter(instance), None) if instance else None
        else:
            first_obj = instance
        
        if first_obj:
            # Ajouter champs conditionnels si annotations présentes
            if hasattr(first_obj, 'total_keywords'):
                self.fields['total_keywords'] = serializers.IntegerField(read_only=True)
            if hasattr(first_obj, 'unique_keywords'):
                self.fields['unique_keywords'] = serializers.IntegerField(read_only=True)
            if hasattr(first_obj, 'avg_sitemap_priority'):
                self.fields['avg_sitemap_priority'] = serializers.FloatField(read_only=True)
            if hasattr(first_obj, 'published_pages'):
                self.fields['published_pages'] = serializers.IntegerField(read_only=True)
            if hasattr(first_obj, 'draft_pages'):
                self.fields['draft_pages'] = serializers.IntegerField(read_only=True)
            if hasattr(first_obj, 'total_sections'):
                self.fields['total_sections'] = serializers.IntegerField(read_only=True)
            if hasattr(first_obj, 'pages_with_layout'):
                self.fields['pages_with_layout'] = serializers.IntegerField(read_only=True)
            if hasattr(first_obj, 'excluded_pages'):
                self.fields['excluded_pages'] = serializers.IntegerField(read_only=True)
    
    def get_pages_count(self, obj):
        """Nombre de pages (optimisé si préchargé via annotation)"""
        if hasattr(obj, 'pages_count'):
            return obj.pages_count
        return obj.get_pages_count()
    
    # ===== STATS CALCULÉES (via StatsMixin) =====
    
    def get_keywords_ratio(self, obj):
        """Ratio mots-clés / pages"""
        if hasattr(obj, 'total_keywords') and hasattr(obj, 'pages_count'):
            if obj.pages_count > 0:
                return round(obj.total_keywords / obj.pages_count, 2)
        return 0
    
    def get_publication_ratio(self, obj):
        """Ratio pages publiées / total"""
        if hasattr(obj, 'published_pages') and hasattr(obj, 'pages_count'):
            if obj.pages_count > 0:
                return round(obj.published_pages / obj.pages_count, 2)
        return 0
    
    def get_layout_coverage(self, obj):
        """Ratio pages avec layout / total"""
        if hasattr(obj, 'pages_with_layout') and hasattr(obj, 'pages_count'):
            if obj.pages_count > 0:
                return round(obj.pages_with_layout / obj.pages_count, 2)
        return 0
    
    def get_seo_coverage(self, obj):
        """Ratio pages avec config SEO / total"""
        if hasattr(obj, 'excluded_pages') and hasattr(obj, 'pages_count'):
            if obj.pages_count > 0:
                seo_pages = obj.pages_count - obj.excluded_pages
                return round(seo_pages / obj.pages_count, 2)
        return 0
    
    def get_performance_score(self, obj):
        """Score de performance global (0-100)"""
        score = 0
        
        # DA Score (40%)
        if obj.domain_authority:
            da_score = min(obj.domain_authority / 100 * 40, 40)
            score += da_score
        
        # Publication Score (30%)
        pub_ratio = self.get_publication_ratio(obj)
        score += pub_ratio * 30
        
        # Keywords Score (20%)  
        kw_ratio = self.get_keywords_ratio(obj)
        if kw_ratio > 0:
            kw_score = min(kw_ratio * 20, 20)  # Cap à 20 points
            score += kw_score
        
        # Layout Score (10%)
        layout_ratio = self.get_layout_coverage(obj)
        score += layout_ratio * 10
        
        return round(score, 1)


class WebsiteDetailSerializer(DynamicFieldsSerializer, WebsiteCoreBaseSerializer):
    """Serializer pour détail website - données complètes"""
    
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_id = serializers.IntegerField(source='brand.id', read_only=True)
    brand_chatgpt_key = serializers.SerializerMethodField()
    brand_gemini_key = serializers.SerializerMethodField()
    pages_count = serializers.SerializerMethodField()
    
    # Relations quick access
    brand_admin_name = serializers.CharField(
        source='brand.brand_admin.username', 
        read_only=True
    )
    company_name = serializers.CharField(
        source='brand.company.name', 
        read_only=True
    )
    
    class Meta:
        model = Website
        fields = '__all__'
    
    def get_pages_count(self, obj):
        return obj.get_pages_count()
    
    def get_brand_chatgpt_key(self, obj):
        """Indique si la brand a une clé ChatGPT (sans exposer la clé)"""
        return bool(obj.brand.chatgpt_key)
    
    def get_brand_gemini_key(self, obj):
        """Indique si la brand a une clé Gemini (sans exposer la clé)"""
        return bool(obj.brand.gemini_key)


class WebsiteCreateSerializer(WebsiteCoreBaseSerializer):
    """Serializer pour création/modification website"""
    
    class Meta:
        model = Website
        fields = [
            'name', 'url', 'brand', 'domain_authority', 
            'max_competitor_backlinks', 'max_competitor_kd'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'url': {'required': True},
            'brand': {'required': True},
            'domain_authority': {'required': False, 'min_value': 0, 'max_value': 100},
            'max_competitor_backlinks': {'required': False, 'min_value': 0},
            'max_competitor_kd': {'required': False, 'min_value': 0.0, 'max_value': 1.0}
        }
    
    def validate_name(self, value):
        """Validation nom du site"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Le nom du site doit contenir au moins 3 caractères"
            )
        return value.strip()
    
    def validate_url(self, value):
        """Validation URL du site"""
        # Ajouter https:// si pas de protocole
        if not value.startswith(('http://', 'https://')):
            value = f"https://{value}"
        
        # Validation basique format URL
        from django.core.validators import URLValidator
        validator = URLValidator()
        try:
            validator(value)
        except:
            raise serializers.ValidationError("Format d'URL invalide")
        
        return value
    
    def validate_brand(self, value):
        """Vérifier que la brand appartient à la company de l'user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user_company = getattr(request.user, 'company', None)
            if user_company and value.company != user_company:
                raise serializers.ValidationError(
                    "Cette brand n'appartient pas à votre company"
                )
        return value
    
    def validate_domain_authority(self, value):
        """Validation Domain Authority"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "Le Domain Authority doit être entre 0 et 100"
            )
        return value
    
    def validate_max_competitor_kd(self, value):
        """Validation Keyword Difficulty max"""
        if value is not None and (value < 0 or value > 1):
            raise serializers.ValidationError(
                "La difficulté max doit être entre 0.0 et 1.0"
            )
        return value
    
    def validate(self, attrs):
        """Validation globale des données"""
        # Vérifier cohérence DA vs KD max
        da = attrs.get('domain_authority')
        max_kd = attrs.get('max_competitor_kd')
        
        if da and max_kd:
            # Si DA faible mais KD max élevé = incohérent
            if da < 30 and max_kd > 0.7:
                raise serializers.ValidationError({
                    'max_competitor_kd': 
                    "KD max élevé incohérent avec un DA faible"
                })
        
        # Vérifier unicité URL (si nouveau site)
        url = attrs.get('url')
        if url and not self.instance:
            existing = Website.objects.filter(url=url).first()
            if existing:
                raise serializers.ValidationError({
                    'url': f"Cette URL est déjà utilisée par le site '{existing.name}'"
                })
        
        return super().validate(attrs)