# backend/blog_editor/serializers/editor_serializers.py

from rest_framework import serializers
from common.serializers.mixins import TimestampedSerializer
from common.serializers.mixins import StatsMixin
from common.serializers.mixins import StatsMixin
from ..models import BlogContent


class BlogContentSerializer(TimestampedSerializer):
    """Contenu TipTap - Version tracking et édition"""
    
    # Champs Article read-only
    article_title = serializers.CharField(source='article.page.title', read_only=True)
    article_author = serializers.CharField(source='article.primary_author.get_full_name', read_only=True)
    last_editor_name = serializers.CharField(source='last_edited_by.get_full_name', read_only=True)
    
    class Meta:
        model = BlogContent
        fields = '__all__'
        
        field_config = {
            'list': [
                'id', 'article_title', 'article_author', 'version',
                'last_editor_name', 'updated_at'
            ],
            'detail': '__all__',
            'create': ['article', 'content_tiptap'],
            'update': ['content_tiptap', 'content_html', 'content_text']
        }
        
        stats_fields = {
            'word_count_calculated': '_get_word_count',
            'reading_time_calculated': '_get_reading_time'
        }
        
        read_only_fields = ['created_at', 'updated_at', 'version', 'last_edited_by']
    
    def _get_word_count(self, obj):
        """Calcul automatique mots depuis content_text"""
        if obj.content_text:
            return len(obj.content_text.split())
        return 0
    
    def _get_reading_time(self, obj):
        """Calcul temps lecture (250 mots/min)"""
        word_count = self._get_word_count(obj)
        return max(1, round(word_count / 250))
    
    def update(self, instance, validated_data):
        """Auto-increment version + last_editor"""
        if 'content_tiptap' in validated_data:
            instance.version += 1
            instance.last_edited_by = self.context['request'].user
        return super().update(instance, validated_data)


class BlogContentAutosaveSerializer(serializers.ModelSerializer):
    """Serializer allégé pour autosave"""
    
    class Meta:
        model = BlogContent
        fields = ['content_tiptap', 'content_html', 'content_text']