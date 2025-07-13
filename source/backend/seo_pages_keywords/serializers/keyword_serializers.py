# backend/seo_pages_keywords/serializers/keyword_serializers.py

from rest_framework import serializers

from .base_serializers import PageKeywordsBaseSerializer
from ..models import PageKeyword

class PageKeywordListSerializer(PageKeywordsBaseSerializer):
    """Serializer liste associations page-keyword"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    keyword_type_display = serializers.CharField(source='get_keyword_type_display', read_only=True)
    source_cocoon_name = serializers.CharField(source='source_cocoon.name', read_only=True)
    
    class Meta:
        model = PageKeyword
        fields = [
            'id', 'page', 'page_title', 'page_url',
            'keyword', 'keyword_text', 'keyword_volume',
            'keyword_type', 'keyword_type_display', 'position',
            'source_cocoon', 'source_cocoon_name', 'is_ai_selected'
        ]

class PageKeywordDetailSerializer(PageKeywordsBaseSerializer):
    """Serializer détail association avec métriques complètes"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    keyword_text = serializers.CharField(source='keyword.keyword', read_only=True)
    keyword_volume = serializers.IntegerField(source='keyword.volume', read_only=True)
    keyword_search_intent = serializers.CharField(source='keyword.search_intent', read_only=True)
    keyword_type_display = serializers.CharField(source='get_keyword_type_display', read_only=True)
    source_cocoon_name = serializers.CharField(source='source_cocoon.name', read_only=True)
    keyword_difficulty = serializers.SerializerMethodField()
    
    class Meta:
        model = PageKeyword
        fields = [
            'id', 'page', 'page_title', 'page_url',
            'keyword', 'keyword_text', 'keyword_volume', 'keyword_search_intent',
            'keyword_type', 'keyword_type_display', 'position',
            'source_cocoon', 'source_cocoon_name', 'is_ai_selected',
            'keyword_difficulty', 'notes', 'created_at', 'updated_at'
        ]
    
    def get_keyword_difficulty(self, obj):
        return obj.get_keyword_difficulty()

class PageKeywordCreateSerializer(PageKeywordsBaseSerializer):
    """Serializer création association page-keyword"""
    
    class Meta:
        model = PageKeyword
        fields = [
            'id',  # ✅ AJOUT : L'ID est nécessaire pour la réponse après création
            'page', 'keyword', 'keyword_type', 'position',
            'source_cocoon', 'is_ai_selected', 'notes'
        ]
        # ✅ OPTIONNEL : Spécifier que l'ID est en lecture seule
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validation business rules"""
        page = data.get('page')
        keyword = data.get('keyword')
        keyword_type = data.get('keyword_type')
        
        # Vérifier doublon page/keyword
        existing = PageKeyword.objects.filter(page=page, keyword=keyword)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError({
                'keyword': 'Ce mot-clé est déjà assigné à cette page'
            })
        
        # Un seul mot-clé primaire par page
        if keyword_type == 'primary':
            existing_primary = PageKeyword.objects.filter(
                page=page, 
                keyword_type='primary'
            )
            if self.instance:
                existing_primary = existing_primary.exclude(pk=self.instance.pk)
            
            if existing_primary.exists():
                raise serializers.ValidationError({
                    'keyword_type': 'Une page ne peut avoir qu\'un seul mot-clé primaire'
                })
        
        return data



class PageKeywordBulkCreateSerializer(serializers.Serializer):
    """Serializer création en masse d'associations"""
    
    page = serializers.IntegerField()
    keywords = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_page(self, value):
        """Validation existence page"""
        from seo_pages_content.models import Page
        
        try:
            Page.objects.get(id=value)
        except Page.DoesNotExist:
            raise serializers.ValidationError("Page non trouvée")
        
        return value
    
    def validate_keywords(self, value):
        """Validation structure keywords"""
        from seo_keywords_base.models import Keyword
        
        for keyword_data in value:
            required_fields = ['keyword_id', 'keyword_type']
            for field in required_fields:
                if field not in keyword_data:
                    raise serializers.ValidationError(
                        f"Champ requis manquant: {field}"
                    )
            
            # Vérifier existence keyword
            try:
                Keyword.objects.get(id=keyword_data['keyword_id'])
            except Keyword.DoesNotExist:
                raise serializers.ValidationError(
                    f"Mot-clé non trouvé: {keyword_data['keyword_id']}"
                )
        
        return value

class PageKeywordStatsSerializer(serializers.Serializer):
    """Serializer statistiques mots-clés par page"""
    
    page_id = serializers.IntegerField()
    page_title = serializers.CharField()
    total_keywords = serializers.IntegerField()
    primary_keywords = serializers.IntegerField()
    secondary_keywords = serializers.IntegerField()
    anchor_keywords = serializers.IntegerField()
    ai_selected_count = serializers.IntegerField()
    total_volume = serializers.IntegerField()
    avg_volume = serializers.FloatField()
    cocoons_used = serializers.ListField(child=serializers.CharField())
