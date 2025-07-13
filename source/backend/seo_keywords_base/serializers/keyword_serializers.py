# backend/seo_keywords_base/serializers/keyword_serializers.py

from rest_framework import serializers
from common.serializers.mixins import TimestampedSerializer
from ..models import Keyword

class KeywordListSerializer(TimestampedSerializer):
    """Serializer allégé pour listes de mots-clés"""
    
    # Relations cross-app (ajoutées dynamiquement)
    has_metrics = serializers.SerializerMethodField()
    cocoons_count = serializers.IntegerField(read_only=True, default=0)
    has_ppas = serializers.BooleanField(read_only=True, default=False)
    ppas_count = serializers.IntegerField(read_only=True, default=0)
    content_types_count = serializers.IntegerField(read_only=True, default=0)
    has_content_types = serializers.BooleanField(read_only=True, default=False)
    
    # Métriques
    da_median = serializers.SerializerMethodField()
    bl_median = serializers.SerializerMethodField()
    kdifficulty_normalized = serializers.SerializerMethodField()
    
    # 🔥 AJOUTER LES PPAs (comme dans le DetailSerializer)
    ppas = serializers.SerializerMethodField()
    
    class Meta:
        model = Keyword
        fields = [
            'id', 'keyword', 'volume', 'search_intent', 'cpc',
            'youtube_videos', 'local_pack', 'content_types',
            'has_metrics', 'cocoons_count', 'has_ppas', 'ppas_count', 
            'content_types_count', 'has_content_types',
            'da_median', 'bl_median', 'kdifficulty_normalized',
            # 🔥 AJOUTER
            'ppas',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    # Méthodes existantes...
    def get_has_metrics(self, obj):
        return hasattr(obj, 'metrics') and obj.metrics is not None
    
    def get_da_median(self, obj):
        if hasattr(obj, 'metrics') and obj.metrics:
            return obj.metrics.da_median
        return None
    
    def get_bl_median(self, obj):
        if hasattr(obj, 'metrics') and obj.metrics:
            return obj.metrics.bl_median
        return None
    
    def get_kdifficulty_normalized(self, obj):
        if hasattr(obj, 'metrics') and obj.metrics:
            return obj.metrics.get_normalized_difficulty()
        return None
    
    # 🔥 NOUVELLE MÉTHODE (copie du DetailSerializer)
    def get_ppas(self, obj):
        """PPAs avec positions - VERSION ALLÉGÉE pour listes"""
        try:
            if hasattr(obj, 'ppa_associations'):
                associations = obj.ppa_associations.all()
                return [
                    {
                        'question': assoc.ppa.question,
                        'position': assoc.position
                    }
                    for assoc in associations[:4]  # Limite à 4 pour les listes
                ]
        except Exception as e:
            pass
        return []

class KeywordDetailSerializer(TimestampedSerializer):
    """Serializer complet pour détails avec toutes les relations cross-app"""
    
    # Données de base
    id = serializers.IntegerField(read_only=True)
    keyword = serializers.CharField()
    
    # Relations cross-app (chargées via prefetch_related)
    cocoons = serializers.SerializerMethodField()
    ppas = serializers.SerializerMethodField()
    content_types_relations = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()
    
    # Stats (ajoutées par ViewSet si nécessaire)
    cocoons_stats = serializers.DictField(read_only=True, required=False)
    ppas_stats = serializers.DictField(read_only=True, required=False)
    
    class Meta:
        model = Keyword
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_cocoons(self, obj):
        """Cocons associés avec détails"""
        try:
            if hasattr(obj, 'cocoon_associations'):
                associations = obj.cocoon_associations.all()
                return [
                    {
                        'id': assoc.cocoon.id,
                        'name': assoc.cocoon.name,
                        'slug': getattr(assoc.cocoon, 'slug', ''),
                        'categories': [
                            {
                                'id': cat.id, 
                                'name': cat.name, 
                                'color': getattr(cat, 'color', '#3498db')
                            }
                            for cat in assoc.cocoon.categories.all()
                        ] if hasattr(assoc.cocoon, 'categories') else [],
                        'association_date': assoc.created_at
                    }
                    for assoc in associations
                ]
        except Exception as e:
            # Fallback silencieux si les relations ne sont pas disponibles
            pass
        return []
    
    def get_ppas(self, obj):
        """PPAs avec positions"""
        try:
            if hasattr(obj, 'ppa_associations'):
                associations = obj.ppa_associations.all()
                return [
                    {
                        'id': assoc.ppa.id,
                        'question': assoc.ppa.question,
                        'position': assoc.position,
                        'association_date': assoc.created_at
                    }
                    for assoc in associations
                ]
        except Exception as e:
            pass
        return []
    
    def get_content_types_relations(self, obj):
        """Types de contenu avec priorités"""
        try:
            if hasattr(obj, 'content_type_associations'):
                associations = obj.content_type_associations.all()
                return [
                    {
                        'id': assoc.content_type.id,
                        'name': assoc.content_type.name,
                        'description': assoc.content_type.description or '',
                        'priority': assoc.priority
                    }
                    for assoc in associations
                ]
        except Exception as e:
            pass
        
        # Fallback sur legacy field
        if obj.content_types:
            return [
                {'name': ct.strip(), 'legacy': True} 
                for ct in obj.content_types.split(',') if ct.strip()
            ]
        return []
    
    def get_metrics(self, obj):
        """Métriques complètes si disponibles"""
        try:
            if hasattr(obj, 'metrics') and obj.metrics:
                return {
                    'da_min': obj.metrics.da_min,
                    'da_q1': obj.metrics.da_q1,
                    'da_median': obj.metrics.da_median,
                    'da_q3': obj.metrics.da_q3,
                    'da_max': obj.metrics.da_max,
                    
                    'bl_min': obj.metrics.bl_min,
                    'bl_q1': obj.metrics.bl_q1,
                    'bl_median': obj.metrics.bl_median,
                    'bl_q3': obj.metrics.bl_q3,
                    'bl_max': obj.metrics.bl_max,
                    
                    'kdifficulty': obj.metrics.kdifficulty,
                    'kdifficulty_normalized': obj.metrics.get_normalized_difficulty(),
                    
                    'last_updated': obj.metrics.updated_at
                }
        except Exception as e:
            pass
        return None

class KeywordSerializer(TimestampedSerializer):
    """Serializer standard pour CRUD"""
    
    class Meta:
        model = Keyword
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_keyword(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le mot-clé ne peut pas être vide.")
        return value.strip()