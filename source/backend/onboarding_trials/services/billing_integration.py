# backend/onboarding_trials/services/billing_integration.py
import logging

logger = logging.getLogger(__name__)

def handle_agency_upgrade_billing(company):
    """
    Gère l'aspect billing de l'upgrade agency
    
    Args:
        company (Company): Company upgradée
    """
    try:
        from billing_core.models import Plan, Subscription
        
        # Récupérer plan professional
        try:
            professional_plan = Plan.objects.get(
                plan_type='professional',
                is_active=True
            )
        except Plan.DoesNotExist:
            logger.warning(f"Plan professional non trouvé pour upgrade {company.name}")
            return
        
        # Upgrade subscription si existe
        try:
            subscription = company.subscription
            old_plan = subscription.plan
            
            subscription.plan = professional_plan
            subscription.amount = professional_plan.price
            subscription.save(update_fields=['plan', 'amount'])
            
            logger.info(f"Subscription upgradée pour {company.name}: {old_plan.name} -> {professional_plan.name}")
            
        except AttributeError:
            logger.info(f"Pas de subscription pour {company.name} - skip upgrade billing")
            
    except ImportError:
        logger.info("billing_core non disponible - skip upgrade billing")
    except Exception as e:
        logger.error(f"Erreur upgrade billing pour {company.name}: {str(e)}")

def handle_manual_upgrade_billing(company, plan_type):
    """
    Gère billing pour upgrade manuel
    
    Args:
        company (Company): Company à upgrader
        plan_type (str): Type de plan choisi
    """
    try:
        from billing_core.models import Plan, Subscription
        
        # Récupérer plan choisi
        try:
            new_plan = Plan.objects.get(
                plan_type=plan_type,
                is_active=True
            )
        except Plan.DoesNotExist:
            logger.error(f"Plan {plan_type} non trouvé pour {company.name}")
            return
        
        # Créer ou upgrade subscription
        subscription, created = Subscription.objects.get_or_create(
            company=company,
            defaults={
                'plan': new_plan,
                'status': 'active',
                'started_at': timezone.now(),
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30),
                'amount': new_plan.price
            }
        )
        
        if not created:
            # Upgrade existing
            subscription.plan = new_plan
            subscription.amount = new_plan.price
            subscription.status = 'active'
            subscription.save(update_fields=['plan', 'amount', 'status'])
        
        logger.info(f"Manual upgrade billing pour {company.name}: plan {plan_type}")
        
    except ImportError:
        logger.info("billing_core non disponible - skip manual upgrade billing")
    except Exception as e:
        logger.error(f"Erreur manual upgrade billing pour {company.name}: {str(e)}")

def get_billing_upgrade_summary(company):
    """
    Résumé billing upgrade pour company
    
    Args:
        company (Company): Company à analyser
        
    Returns:
        dict: Résumé billing
    """
    try:
        from billing_core.models import Plan
        
        current_plan = None
        try:
            current_plan = company.subscription.plan
        except:
            pass
        
        # Plans disponibles pour upgrade
        available_plans = Plan.objects.filter(
            is_active=True
        ).exclude(
            id=current_plan.id if current_plan else None
        ).order_by('price')
        
        return {
            'current_plan': {
                'name': current_plan.name if current_plan else None,
                'price': current_plan.price if current_plan else 0
            },
            'available_plans': [
                {
                    'plan_type': plan.plan_type,
                    'name': plan.name,
                    'price': plan.price,
                    'features': plan.get_features_summary()
                }
                for plan in available_plans
            ]
        }
        
    except ImportError:
        return {'error': 'billing_core non disponible'}
    except Exception as e:
        logger.error(f"Erreur billing upgrade summary {company.name}: {str(e)}")
        return {'error': str(e)}