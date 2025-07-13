# backend/onboarding_business/services/features_setup.py

from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def setup_default_features(company):
    """
    Setup des features par défaut pour une company
    
    Args:
        company (Company): Company à configurer
        
    Returns:
        list: Liste des CompanyFeature créées
    """
    try:
        from company_features.models import Feature, CompanyFeature
        
        default_features = [
            'websites',   # Feature principale
            'templates',  # Templates IA
            'analytics'   # Analytics de base
        ]
        
        created_features = []
        
        for feature_name in default_features:
            try:
                feature = Feature.objects.get(name=feature_name, is_active=True)
                
                company_feature = CompanyFeature.objects.create(
                    company=company,
                    feature=feature,
                    is_enabled=True,
                    usage_limit=None,  # Illimité pendant trial
                    current_usage=0,
                    expires_at=company.trial_expires_at  # Expire avec trial
                )
                
                created_features.append(company_feature)
                logger.debug(f"Feature {feature_name} activée pour {company.name}")
                
            except Feature.DoesNotExist:
                logger.warning(f"Feature {feature_name} non trouvée - skip")
                continue
            except Exception as e:
                logger.error(f"Erreur setup feature {feature_name} pour {company.name}: {str(e)}")
                continue
        
        logger.info(f"Features setup terminé: {len(created_features)} features pour {company.name}")
        return created_features
        
    except ImportError:
        logger.info("company_features non disponible - skip features setup")
        return []
    except Exception as e:
        logger.error(f"Erreur setup features pour {company.name}: {str(e)}")
        return []


def get_company_features_summary(company):
    """
    Résumé des features actives pour une company
    
    Args:
        company (Company): Company à analyser
        
    Returns:
        dict: Résumé des features
    """
    try:
        from company_features.models import CompanyFeature
        
        features = company.company_features.filter(is_enabled=True).select_related('feature')
        
        return {
            'total_features': features.count(),
            'active_features': [
                {
                    'name': cf.feature.name,
                    'display_name': cf.feature.display_name,
                    'is_premium': cf.feature.is_premium,
                    'usage_limit': cf.usage_limit,
                    'current_usage': cf.current_usage,
                    'usage_percentage': cf.get_usage_percentage(),
                    'expires_at': cf.expires_at,
                    'is_active': cf.is_active()
                }
                for cf in features
            ]
        }
        
    except ImportError:
        return {'total_features': 0, 'active_features': []}
    except Exception as e:
        logger.error(f"Erreur résumé features pour {company.name}: {str(e)}")
        return {'total_features': 0, 'active_features': [], 'error': str(e)}


def extend_trial_features(company, new_trial_end):
    """
    Étend la durée des features trial
    
    Args:
        company (Company): Company concernée
        new_trial_end (datetime): Nouvelle date fin trial
        
    Returns:
        int: Nombre de features étendues
    """
    try:
        updated_count = company.company_features.filter(
            expires_at=company.trial_expires_at
        ).update(expires_at=new_trial_end)
        
        logger.info(f"Trial features étendues: {updated_count} features pour {company.name}")
        return updated_count
        
    except Exception as e:
        logger.error(f"Erreur extension features pour {company.name}: {str(e)}")
        return 0