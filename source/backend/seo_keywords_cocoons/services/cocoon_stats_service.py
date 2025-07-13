# backend/seo_keywords_cocoons/services/cocoon_stats_service.py

from django.db.models import Avg, Sum, Max, Min, Count, Q
from django.core.exceptions import ObjectDoesNotExist
from ..models import SemanticCocoon

import logging
logger = logging.getLogger(__name__)

class CocoonStatsService:
    """Service pour calculs statistiques avancés des cocons"""
    
    @staticmethod
    def get_cocoon_stats(cocoon_id: int) -> dict:
        """
        Calcule toutes les statistiques d'un cocon
        
        Returns:
            dict: Stats complètes avec métriques mots-clés et distribution
        """
        try:
            cocoon = SemanticCocoon.objects.select_related().prefetch_related(
                'categories', 
                'cocoon_keywords__keyword'
            ).get(id=cocoon_id)
            
            # Stats de base
            base_stats = {
                'id': cocoon.id,
                'name': cocoon.name,
                'keywords_count': cocoon.cocoon_keywords.count(),
                'categories_count': cocoon.categories.count(),
                'needs_sync': cocoon.needs_sync(),
                'last_sync': cocoon.last_pushed_at,
            }
            
            # Stats avancées si mots-clés présents
            if base_stats['keywords_count'] > 0:
                keyword_metrics = CocoonStatsService._calculate_keyword_metrics(cocoon)
                intent_distribution = CocoonStatsService._calculate_intent_distribution(cocoon)
                volume_ranges = CocoonStatsService._calculate_volume_ranges(cocoon)
                
                base_stats.update({
                    **keyword_metrics,
                    'intent_distribution': intent_distribution,
                    'volume_ranges': volume_ranges
                })
            
            logger.info(f"Stats calculated for cocoon {cocoon_id} - {base_stats['keywords_count']} keywords")
            return base_stats
            
        except SemanticCocoon.DoesNotExist:
            logger.warning(f"Cocoon {cocoon_id} not found")
            raise ValueError(f"Cocon {cocoon_id} introuvable")
        except Exception as e:
            logger.error(f"Error calculating stats for cocoon {cocoon_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _calculate_keyword_metrics(cocoon):
        """Métriques numériques des mots-clés"""
        metrics = cocoon.cocoon_keywords.aggregate(
            avg_volume=Avg('keyword__volume'),
            total_volume=Sum('keyword__volume'),
            max_volume=Max('keyword__volume'),
            min_volume=Min('keyword__volume'),
            keywords_with_volume=Count('keyword', filter=Q(keyword__volume__isnull=False))
        )
        
        # Arrondir les moyennes
        if metrics['avg_volume']:
            metrics['avg_volume'] = round(metrics['avg_volume'], 0)
        
        return metrics
    
    @staticmethod  
    def _calculate_intent_distribution(cocoon):
        """Distribution par intention de recherche"""
        distribution = list(
            cocoon.cocoon_keywords
            .values('keyword__search_intent')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Nettoyer les noms d'intentions
        for item in distribution:
            intent = item['keyword__search_intent']
            item['intent_label'] = {
                'TOFU': 'Top of Funnel',
                'MOFU': 'Middle of Funnel', 
                'BOFU': 'Bottom of Funnel'
            }.get(intent, intent or 'Non défini')
        
        return distribution
    
    @staticmethod
    def _calculate_volume_ranges(cocoon):
        """Répartition par tranches de volume"""
        ranges = {
            'low': cocoon.cocoon_keywords.filter(keyword__volume__lt=1000).count(),
            'medium': cocoon.cocoon_keywords.filter(
                keyword__volume__gte=1000, 
                keyword__volume__lt=10000
            ).count(),
            'high': cocoon.cocoon_keywords.filter(keyword__volume__gte=10000).count(),
            'no_volume': cocoon.cocoon_keywords.filter(keyword__volume__isnull=True).count()
        }
        
        return ranges
    
    @staticmethod
    def get_cocoons_overview() -> dict:
        """Vue d'ensemble de tous les cocons"""
        try:
            total_cocoons = SemanticCocoon.objects.count()
            cocoons_with_keywords = SemanticCocoon.objects.filter(
                cocoon_keywords__isnull=False
            ).distinct().count()
            
            # Top 5 des cocons les plus fournis
            top_cocoons = list(
                SemanticCocoon.objects.annotate(
                    kw_count=Count('cocoon_keywords')
                ).filter(kw_count__gt=0).order_by('-kw_count')[:5]
                .values('id', 'name', 'kw_count')
            )
            
            return {
                'total_cocoons': total_cocoons,
                'cocoons_with_keywords': cocoons_with_keywords,
                'cocoons_empty': total_cocoons - cocoons_with_keywords,
                'top_cocoons': top_cocoons
            }
            
        except Exception as e:
            logger.error(f"Error calculating cocoons overview: {e}", exc_info=True)
            raise