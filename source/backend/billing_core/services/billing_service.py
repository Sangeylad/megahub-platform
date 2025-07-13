# backend/billing_core/services/billing_service.py
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from billing_core.models.billing import Plan, Subscription, Invoice, InvoiceItem, UsageAlert

class BillingService:
    """Service principal pour la gestion de la facturation"""
    
    @staticmethod
    def create_subscription(company, plan, start_date=None, trial_days=None):
        """Crée un nouvel abonnement pour une entreprise"""
        if start_date is None:
            start_date = timezone.now()
        
        # Vérifier qu'il n'y a pas déjà un abonnement actif
        existing_subscription = Subscription.objects.filter(
            company=company, 
            status__in=['active', 'trialing']
        ).first()
        
        if existing_subscription:
            raise ValidationError(f"L'entreprise {company.name} a déjà un abonnement actif")
        
        # Calculer les dates
        if plan.billing_interval == 'monthly':
            from dateutil.relativedelta import relativedelta
            current_period_end = start_date + relativedelta(months=1)
        elif plan.billing_interval == 'yearly':
            from dateutil.relativedelta import relativedelta
            current_period_end = start_date + relativedelta(years=1)
        else:
            current_period_end = start_date  # One-time
        
        # Période d'essai
        trial_end = None
        if trial_days:
            from datetime import timedelta
            trial_end = start_date + timedelta(days=trial_days)
        
        # Créer l'abonnement
        subscription = Subscription.objects.create(
            company=company,
            plan=plan,
            status='trialing' if trial_end else 'active',
            started_at=start_date,
            current_period_start=start_date,
            current_period_end=current_period_end,
            trial_end=trial_end,
            amount=plan.price
        )
        
        # Mettre à jour les slots de l'entreprise
        BillingService.update_company_slots(company, plan)
        
        return subscription
    
    @staticmethod
    def update_company_slots(company, plan):
        """Met à jour les slots de l'entreprise selon le plan"""
        from company_slots.models.slots import CompanySlots
        
        slots, created = CompanySlots.objects.get_or_create(
            company=company,
            defaults={
                'brands_slots': plan.included_brands_slots,
                'users_slots': plan.included_users_slots,
            }
        )
        
        if not created:
            slots.brands_slots = plan.included_brands_slots
            slots.users_slots = plan.included_users_slots
            slots.save(update_fields=['brands_slots', 'users_slots'])
        
        return slots
    
    @staticmethod
    def calculate_invoice_amount(company, plan, period_start, period_end):
        """Calcule le montant d'une facture selon l'utilisation"""
        try:
            slots = company.slots
            
            # Montant de base du plan
            base_amount = plan.price
            
            # Calcul des suppléments
            additional_brands = max(0, slots.current_brands_count - plan.included_brands_slots)
            additional_users = max(0, slots.current_users_count - plan.included_users_slots)
            
            additional_amount = (
                (additional_brands * plan.additional_brand_price) +
                (additional_users * plan.additional_user_price)
            )
            
            return {
                'base_amount': base_amount,
                'additional_amount': additional_amount,
                'total_amount': base_amount + additional_amount,
                'additional_brands': additional_brands,
                'additional_users': additional_users,
            }
        except:
            return {
                'base_amount': plan.price,
                'additional_amount': Decimal('0.00'),
                'total_amount': plan.price,
                'additional_brands': 0,
                'additional_users': 0,
            }
    
    @staticmethod
    def generate_invoice(subscription, invoice_date=None):
        """Génère une facture pour un abonnement"""
        if invoice_date is None:
            invoice_date = timezone.now()
        
        company = subscription.company
        plan = subscription.plan
        
        # Calculer le montant
        amounts = BillingService.calculate_invoice_amount(
            company, plan, 
            subscription.current_period_start, 
            subscription.current_period_end
        )
        
        # Générer le numéro de facture
        invoice_number = BillingService.generate_invoice_number(company)
        
        # Créer la facture
        invoice = Invoice.objects.create(
            company=company,
            subscription=subscription,
            invoice_number=invoice_number,
            status='open',
            subtotal=amounts['total_amount'],
            tax_amount=Decimal('0.00'),  # À calculer selon la juridiction
            total=amounts['total_amount'],
            invoice_date=invoice_date,
            due_date=invoice_date + timezone.timedelta(days=30),
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
        )
        
        # Créer les lignes de facture
        BillingService.create_invoice_items(invoice, plan, amounts)
        
        return invoice
    
    @staticmethod
    def create_invoice_items(invoice, plan, amounts):
        """Crée les lignes de facture"""
        items = []
        
        # Ligne pour le plan de base
        items.append(InvoiceItem.objects.create(
            invoice=invoice,
            description=f"Plan {plan.display_name} - {plan.get_billing_interval_display()}",
            quantity=1,
            unit_price=plan.price,
            item_type='plan'
        ))
        
        # Lignes pour les suppléments
        if amounts['additional_brands'] > 0:
            items.append(InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Marques supplémentaires ({amounts['additional_brands']})",
                quantity=amounts['additional_brands'],
                unit_price=plan.additional_brand_price,
                item_type='additional_brand'
            ))
        
        if amounts['additional_users'] > 0:
            items.append(InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Utilisateurs supplémentaires ({amounts['additional_users']})",
                quantity=amounts['additional_users'],
                unit_price=plan.additional_user_price,
                item_type='additional_user'
            ))
        
        return items
    
    @staticmethod
    def generate_invoice_number(company):
        """Génère un numéro de facture unique"""
        from datetime import datetime
        
        # Format: COMP-YYYY-MM-0001
        now = datetime.now()
        prefix = f"{company.name[:4].upper()}-{now.year}-{now.month:02d}"
        
        # Trouver le prochain numéro
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f"{prefix}-{next_number:04d}"
    
    @staticmethod
    def check_usage_limits(company):
        """Vérifie les limites d'utilisation et génère des alertes"""
        try:
            slots = company.slots
            alerts = []
            
            # Vérifier les limites brands
            brands_usage = slots.get_brands_usage_percentage()
            if brands_usage >= 100:
                alert = UsageAlert.objects.create(
                    company=company,
                    alert_type='brands_limit',
                    message=f"Limite de marques atteinte ({slots.current_brands_count}/{slots.brands_slots})"
                )
                alerts.append(alert)
            elif brands_usage >= 80:
                alert = UsageAlert.objects.create(
                    company=company,
                    alert_type='brands_warning',
                    message=f"Limite de marques bientôt atteinte ({slots.current_brands_count}/{slots.brands_slots})"
                )
                alerts.append(alert)
            
            # Vérifier les limites users
            users_usage = slots.get_users_usage_percentage()
            if users_usage >= 100:
                alert = UsageAlert.objects.create(
                    company=company,
                    alert_type='users_limit',
                    message=f"Limite d'utilisateurs atteinte ({slots.current_users_count}/{slots.users_slots})"
                )
                alerts.append(alert)
            elif users_usage >= 80:
                alert = UsageAlert.objects.create(
                    company=company,
                    alert_type='users_warning',
                    message=f"Limite d'utilisateurs bientôt atteinte ({slots.current_users_count}/{slots.users_slots})"
                )
                alerts.append(alert)
            
            return alerts
        except:
            return []
    
    @staticmethod
    def cancel_subscription(subscription, cancel_at_period_end=True):
        """Annule un abonnement"""
        if cancel_at_period_end:
            # Annulation à la fin de la période
            subscription.canceled_at = subscription.current_period_end
        else:
            # Annulation immédiate
            subscription.canceled_at = timezone.now()
            subscription.status = 'canceled'
        
        subscription.save()
        return subscription
    
    @staticmethod
    def upgrade_subscription(subscription, new_plan):
        """Change le plan d'un abonnement"""
        old_plan = subscription.plan
        
        # Calculer le prorata
        prorata_amount = BillingService.calculate_prorata(
            subscription, old_plan, new_plan
        )
        
        # Mettre à jour l'abonnement
        subscription.plan = new_plan
        subscription.amount = new_plan.price
        subscription.save()
        
        # Mettre à jour les slots
        BillingService.update_company_slots(subscription.company, new_plan)
        
        # Générer une facture de prorata si nécessaire
        if prorata_amount > 0:
            BillingService.generate_prorata_invoice(subscription, prorata_amount)
        
        return subscription
    
    @staticmethod
    def calculate_prorata(subscription, old_plan, new_plan):
        """Calcule le prorata lors d'un changement de plan"""
        # Logique de calcul de prorata
        # Simplifié pour l'exemple
        price_diff = new_plan.price - old_plan.price
        
        # Calculer les jours restants
        now = timezone.now()
        total_days = (subscription.current_period_end - subscription.current_period_start).days
        remaining_days = (subscription.current_period_end - now).days
        
        if remaining_days > 0:
            prorata = (price_diff * remaining_days) / total_days
            return max(prorata, Decimal('0.00'))
        
        return Decimal('0.00')
    
    @staticmethod
    def generate_prorata_invoice(subscription, prorata_amount):
        """Génère une facture de prorata"""
        # Implémentation simplifiée
        pass
    
    @staticmethod
    def get_billing_summary(company):
        """Résumé de facturation pour une entreprise"""
        try:
            subscription = company.subscription
            slots = company.slots
            
            return {
                'company': company.name,
                'plan': subscription.plan.display_name,
                'status': subscription.get_status_display(),
                'current_period_end': subscription.current_period_end,
                'amount': subscription.amount,
                'slots': {
                    'brands': f"{slots.current_brands_count}/{slots.brands_slots}",
                    'users': f"{slots.current_users_count}/{slots.users_slots}",
                },
                'next_invoice_date': subscription.current_period_end,
                'days_until_renewal': subscription.days_until_renewal(),
            }
        except:
            return {
                'company': company.name,
                'plan': None,
                'status': 'Aucun abonnement',
                'error': 'Données de facturation indisponibles'
            }
