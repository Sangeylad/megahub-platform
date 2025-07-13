# backend/blog_editor/services/tiptap_service.py

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TipTapService:
    """Service spécialisé pour conversions TipTap"""
    
    @staticmethod
    def convert_tiptap_to_html(tiptap_json: Dict[str, Any]) -> str:
        """Convertit TipTap JSON vers HTML propre"""
        if not tiptap_json:
            return ""
        
        try:
            def extract_html_from_node(node):
                if not isinstance(node, dict):
                    return ""
                
                node_type = node.get('type', '')
                content = node.get('content', [])
                text = node.get('text', '')
                attrs = node.get('attrs', {})
                marks = node.get('marks', [])
                
                # Gérer le texte avec marques
                if text:
                    result_text = text
                    for mark in marks:
                        mark_type = mark.get('type', '')
                        if mark_type == 'bold':
                            result_text = f'<strong>{result_text}</strong>'
                        elif mark_type == 'italic':
                            result_text = f'<em>{result_text}</em>'
                        elif mark_type == 'code':
                            result_text = f'<code>{result_text}</code>'
                        elif mark_type == 'link':
                            href = mark.get('attrs', {}).get('href', '')
                            result_text = f'<a href="{href}">{result_text}</a>'
                    return result_text
                
                # Traiter enfants
                html_parts = []
                for child in content:
                    html_parts.append(extract_html_from_node(child))
                
                inner_html = ''.join(html_parts)
                
                # Mapping nœuds vers HTML
                if node_type == 'paragraph':
                    return f'<p>{inner_html}</p>'
                elif node_type == 'heading':
                    level = attrs.get('level', 2)
                    return f'<h{level}>{inner_html}</h{level}>'
                elif node_type == 'bulletList':
                    return f'<ul>{inner_html}</ul>'
                elif node_type == 'orderedList':
                    return f'<ol>{inner_html}</ol>'
                elif node_type == 'listItem':
                    return f'<li>{inner_html}</li>'
                elif node_type == 'blockquote':
                    return f'<blockquote>{inner_html}</blockquote>'
                elif node_type == 'codeBlock':
                    language = attrs.get('language', '')
                    if language:
                        return f'<pre><code class="language-{language}">{inner_html}</code></pre>'
                    return f'<pre><code>{inner_html}</code></pre>'
                elif node_type == 'hardBreak':
                    return '<br>'
                elif node_type == 'image':
                    src = attrs.get('src', '')
                    alt = attrs.get('alt', '')
                    title = attrs.get('title', '')
                    if title:
                        return f'<img src="{src}" alt="{alt}" title="{title}" />'
                    return f'<img src="{src}" alt="{alt}" />'
                elif node_type == 'horizontalRule':
                    return '<hr>'
                else:
                    return f'<div>{inner_html}</div>' if inner_html else ''
            
            return extract_html_from_node(tiptap_json)
            
        except Exception as e:
            logger.error(f"Erreur conversion TipTap: {str(e)}")
            return f"<!-- Erreur conversion: {str(e)} -->"
    
    @staticmethod
    def extract_text_from_tiptap(tiptap_json: Dict[str, Any]) -> str:
        """Extrait le texte brut depuis TipTap JSON"""
        if not tiptap_json:
            return ""
        
        try:
            def extract_text_from_node(node):
                if not isinstance(node, dict):
                    return ""
                
                text = node.get('text', '')
                if text:
                    return text
                
                content = node.get('content', [])
                text_parts = []
                for child in content:
                    child_text = extract_text_from_node(child)
                    if child_text:
                        text_parts.append(child_text)
                
                # Ajouter espaces entre blocs
                node_type = node.get('type', '')
                if node_type in ['paragraph', 'heading', 'listItem']:
                    return ' '.join(text_parts) + '\n'
                else:
                    return ' '.join(text_parts)
            
            text = extract_text_from_node(tiptap_json)
            # Nettoyer espaces multiples
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erreur extraction texte: {str(e)}")
            return ""
    
    @staticmethod
    def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
        """Calcule le temps de lecture estimé"""
        if not text:
            return 1
        
        word_count = len(text.split())
        reading_time = max(1, word_count // words_per_minute)
        return reading_time
    
    @staticmethod
    def update_article_content(article, tiptap_json: Dict[str, Any], user=None) -> None:
        """Met à jour le contenu d'un article avec TipTap"""
        from ..models import BlogContent
        
        # Créer ou récupérer BlogContent
        content, created = BlogContent.objects.get_or_create(
            article=article,
            defaults={'content_tiptap': tiptap_json}
        )
        
        if not created:
            content.content_tiptap = tiptap_json
            content.version += 1
            if user:
                content.last_edited_by = user
        
        # Générer HTML et texte
        content.content_html = TipTapService.convert_tiptap_to_html(tiptap_json)
        content.content_text = TipTapService.extract_text_from_tiptap(tiptap_json)
        content.save()
        
        # Mettre à jour stats article
        article.word_count = len(content.content_text.split()) if content.content_text else 0
        article.reading_time_minutes = TipTapService.calculate_reading_time(content.content_text)
        article.save(update_fields=['word_count', 'reading_time_minutes'])
        
        logger.info(f"Article {article.id} content updated - {article.word_count} words")