# backend/glossary/serializers/term_serializers.py
from rest_framework import serializers
from glossary.models import Term, TermTranslation, TermRelation
from .category_serializers import TermCategoryListSerializer


class TermTranslationSerializer(serializers.ModelSerializer):
    """Serializer pour les traductions des termes"""
    
    class Meta:
        model = TermTranslation
        fields = [
            'language', 'context', 'title', 'definition', 'examples',
            'formula', 'benchmarks', 'sources', 'meta_title', 'meta_description'
        ]


class TermListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des termes (vue compacte)"""
    
    category = TermCategoryListSerializer(read_only=True)
    primary_translation = serializers.SerializerMethodField()
    url_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Term
        fields = [
            'id', 'slug', 'category', 'is_essential', 'difficulty_level',
            'popularity_score', 'primary_translation', 'url_path'
        ]
    
    def get_primary_translation(self, obj):
        # Langue demandée en paramètre, français par défaut
        language = self.context.get('language', 'fr')
        translation = obj.get_translation(language)
        if translation:
            return {
                'title': translation.title,
                'definition': translation.definition[:200] + '...' if len(translation.definition) > 200 else translation.definition,
                'context': translation.context
            }
        return None
    
    def get_url_path(self, obj):
        language = self.context.get('language', 'fr')
        return obj.get_url_path(language)


class TermDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour le détail d'un terme"""
    
    category = TermCategoryListSerializer(read_only=True)
    translations = TermTranslationSerializer(many=True, read_only=True)
    current_translation = serializers.SerializerMethodField()
    related_terms = serializers.SerializerMethodField()
    url_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Term
        fields = [
            'id', 'slug', 'category', 'is_essential', 'difficulty_level',
            'popularity_score', 'is_active', 'translations', 'current_translation',
            'related_terms', 'url_path', 'created_at', 'updated_at'
        ]
    
    def get_current_translation(self, obj):
        language = self.context.get('language', 'fr')
        translation = obj.get_translation(language)
        return TermTranslationSerializer(translation).data if translation else None
    
    def get_related_terms(self, obj):
        # Termes liés via TermRelation
        related = TermRelation.objects.filter(from_term=obj).select_related(
            'to_term__category'  # ✅ Précharger la catégorie
        )
        
        language = self.context.get('language', 'fr')
        
        result = []
        for rel in related:
            to_term = rel.to_term
            translation = to_term.get_translation(language)
            
            result.append({
                'id': to_term.id,
                'slug': to_term.slug,
                'title': translation.title if translation else to_term.slug,
                'category': {  # ✅ AJOUT: données de catégorie
                    'id': to_term.category.id,
                    'name': to_term.category.name,
                    'slug': to_term.category.slug,
                    'url_path': to_term.category.get_url_path()
                },
                'relation_type': rel.relation_type,
                'weight': rel.weight
            })
        
        return result
    
    
    def get_url_path(self, obj):
        language = self.context.get('language', 'fr')
        return obj.get_url_path(language)


class TermSerializer(serializers.ModelSerializer):
    """Serializer de base pour création/modification"""
    
    class Meta:
        model = Term
        fields = [
            'id', 'slug', 'category', 'is_essential', 'difficulty_level',
            'popularity_score', 'is_active'
        ]

class TermCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour création/modification des termes avec traductions"""
    
    translations = TermTranslationSerializer(many=True)
    
    class Meta:
        model = Term
        fields = [
            'slug', 'category', 'is_essential', 'difficulty_level',
            'is_active', 'translations'
        ]
    
    def create(self, validated_data):
        translations_data = validated_data.pop('translations')
        term = Term.objects.create(**validated_data)
        
        for translation_data in translations_data:
            TermTranslation.objects.create(term=term, **translation_data)
        
        return term
    
    def update(self, instance, validated_data):
        translations_data = validated_data.pop('translations', [])
        
        # Mettre à jour le terme
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour/créer les traductions
        for translation_data in translations_data:
            language = translation_data.get('language')
            context = translation_data.get('context', '')
            
            translation, created = TermTranslation.objects.update_or_create(
                term=instance,
                language=language,
                context=context,
                defaults=translation_data
            )
        
        return instance