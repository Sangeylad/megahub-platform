# backend/tests/test_billing_endpoints.py

import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Models
from company_core.models.company import Company
from users_core.models.user import CustomUser
from company_slots.models.slots import CompanySlots
from billing_core.models.billing import Plan, Subscription, Invoice, InvoiceItem, UsageAlert

User = get_user_model()

class PlanEndpointsTestCase(APITestCase):
    """Tests des endpoints Plan"""
    
    def setUp(self):
        """Setup pour tous les tests plans"""
        # Créer admin
        self.admin_user = CustomUser.objects.create_user(
            username='billing_admin',
            email='admin@billing.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        # Créer company
        self.company = Company.objects.create(
            name="Billing Test Company",
            admin=self.admin_user,
            billing_email="billing@billing.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer plans
        self.starter_plan = Plan.objects.create(
            name="starter",
            display_name="Plan Starter",
            description="Plan de base",
            plan_type="starter",
            price=Decimal("29.99"),
            billing_interval="monthly",
            included_brands_slots=3,
            included_users_slots=5,
            additional_brand_price=Decimal("9.99"),
            additional_user_price=Decimal("4.99"),
            is_featured=False
        )
        
        self.pro_plan = Plan.objects.create(
            name="professional",
            display_name="Plan Professional",
            description="Plan professionnel",
            plan_type="professional",
            price=Decimal("99.99"),
            billing_interval="monthly",
            included_brands_slots=10,
            included_users_slots=25,
            additional_brand_price=Decimal("7.99"),
            additional_user_price=Decimal("3.99"),
            is_featured=True
        )
        
        self.client = APIClient()
    
    def test_plans_list_endpoint(self):
        """✅ Test GET /billing/plans/ - Liste des plans"""
        # Test sans auth
        response = self.client.get('/billing/plans/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test avec auth
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/billing/plans/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 2
        
        # Vérifier les champs du serializer list
        plan_data = data['results'][0]
        expected_fields = [
            'id', 'name', 'display_name', 'plan_type', 'price', 'billing_interval',
            'included_brands_slots', 'included_users_slots', 'is_active', 'is_featured',
            'subscriptions_count', 'sort_order'
        ]
        for field in expected_fields:
            assert field in plan_data
        
        print("✅ Plans list endpoint")
    
    def test_plans_detail_endpoint(self):
        """✅ Test GET /billing/plans/{id}/ - Détail plan"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/billing/plans/{self.starter_plan.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['name'] == 'starter'
        assert data['display_name'] == 'Plan Starter'
        assert data['price'] == '29.99'
        assert 'total_price_example' in data
        assert 'features_summary' in data
        assert 'subscriptions_count' in data
        
        # Vérifier features_summary
        assert 'brands_slots' in data['features_summary']
        assert 'users_slots' in data['features_summary']
        assert data['features_summary']['brands_slots'] == 3
        
        print("✅ Plans detail endpoint")
    
    def test_plans_calculate_price_action(self):
        """✅ Test GET /billing/plans/calculate-price/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test calcul de prix pour configuration spécifique
        params = {
            'plan_id': self.starter_plan.id,
            'brands_slots': 5,  # 2 supplémentaires
            'users_slots': 8    # 3 supplémentaires
        }
        
        response = self.client.get('/billing/plans/calculate-price/', params)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['plan'] == 'Plan Starter'
        assert data['base_price'] == '29.99'
        
        # Vérifier le calcul
        expected_additional_brands = 2 * Decimal('9.99')  # 19.98
        expected_additional_users = 3 * Decimal('4.99')   # 14.97
        expected_total = Decimal('29.99') + expected_additional_brands + expected_additional_users
        
        assert Decimal(data['additional_costs']['brands']) == expected_additional_brands
        assert Decimal(data['additional_costs']['users']) == expected_additional_users
        assert Decimal(data['total_price']) == expected_total
        
        # Vérifier breakdown
        assert data['breakdown']['additional_brands'] == 2
        assert data['breakdown']['additional_users'] == 3
        
        print("✅ Plans calculate price action")
    
    def test_plans_calculate_price_validation_errors(self):
        """✅ Test GET /billing/plans/calculate-price/ - Erreurs de validation"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test sans plan_id
        response = self.client.get('/billing/plans/calculate-price/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'plan_id est requis' in response.json()['error']
        
        # Test avec plan inexistant
        params = {'plan_id': 99999, 'brands_slots': 5, 'users_slots': 5}
        response = self.client.get('/billing/plans/calculate-price/', params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test avec valeurs non numériques
        params = {'plan_id': self.starter_plan.id, 'brands_slots': 'invalid', 'users_slots': 5}
        response = self.client.get('/billing/plans/calculate-price/', params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        print("✅ Plans calculate price validation errors")
    
    def test_plans_read_only_viewset(self):
        """✅ Test que PlanViewSet est en lecture seule"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test création interdite
        plan_data = {
            'name': 'forbidden_plan',
            'display_name': 'Forbidden Plan',
            'price': '49.99'
        }
        
        response = self.client.post('/billing/plans/', plan_data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # Test mise à jour interdite
        response = self.client.patch(f'/billing/plans/{self.starter_plan.id}/', {'price': '39.99'})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # Test suppression interdite
        response = self.client.delete(f'/billing/plans/{self.starter_plan.id}/')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        print("✅ Plans read only viewset")


class SubscriptionEndpointsTestCase(APITestCase):
    """Tests des endpoints Subscription"""
    
    def setUp(self):
        """Setup pour tous les tests subscriptions"""
        self.admin_user = CustomUser.objects.create_user(
            username='sub_admin',
            email='admin@sub.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="Subscription Test Company",
            admin=self.admin_user,
            billing_email="billing@sub.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer slots
        self.slots = CompanySlots.objects.create(
            company=self.company,
            brands_slots=5,
            users_slots=10,
            current_brands_count=2,
            current_users_count=3
        )
        
        # Créer plan
        self.plan = Plan.objects.create(
            name="test_plan",
            display_name="Test Plan",
            price=Decimal("49.99"),
            billing_interval="monthly",
            included_brands_slots=5,
            included_users_slots=10
        )
        
        # Créer subscription
        self.subscription = Subscription.objects.create(
            company=self.company,
            plan=self.plan,
            status="active",
            started_at=timezone.now(),
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30),
            amount=self.plan.price
        )
        
        self.client = APIClient()
    
    def test_subscriptions_list_endpoint(self):
        """✅ Test GET /billing/subscriptions/ - Liste des abonnements"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/billing/subscriptions/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1
        
        # Vérifier les champs du serializer list
        sub_data = data['results'][0]
        expected_fields = [
            'id', 'company_name', 'plan_name', 'status', 'amount',
            'current_period_end', 'days_until_renewal', 'created_at'
        ]
        for field in expected_fields:
            assert field in sub_data
        
        assert sub_data['company_name'] == 'Subscription Test Company'
        assert sub_data['plan_name'] == 'Test Plan'
        
        print("✅ Subscriptions list endpoint")
    
    def test_subscriptions_detail_endpoint(self):
        """✅ Test GET /billing/subscriptions/{id}/ - Détail abonnement"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/billing/subscriptions/{self.subscription.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['company_name'] == 'Subscription Test Company'
        assert data['plan_name'] == 'Test Plan'
        assert data['status'] == 'active'
        assert 'is_active_status' in data
        assert 'is_trial_status' in data
        assert 'days_until_renewal' in data
        assert 'usage_summary' in data
        
        # Vérifier usage_summary
        if data['usage_summary']:
            assert 'brands_used' in data['usage_summary']
            assert 'users_used' in data['usage_summary']
        
        print("✅ Subscriptions detail endpoint")
    
    def test_subscriptions_create_endpoint(self):
        """✅ Test POST /billing/subscriptions/ - Création abonnement"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer nouvelle company sans abonnement
        new_company = Company.objects.create(
            name="New Company",
            admin=self.admin_user,
            billing_email="new@test.com"
        )
        
        subscription_data = {
            'company_id': new_company.id,
            'plan_id': self.plan.id,
            'trial_days': 30
        }
        
        response = self.client.post('/billing/subscriptions/', subscription_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Vérifier que l'abonnement est créé
        assert Subscription.objects.filter(company=new_company).exists()
        new_subscription = Subscription.objects.get(company=new_company)
        assert new_subscription.plan == self.plan
        assert new_subscription.status == 'trialing'  # Avec trial_days
        
        print("✅ Subscriptions create endpoint")
    
    def test_subscriptions_cancel_action(self):
        """✅ Test POST /billing/subscriptions/{id}/cancel/"""
        self.client.force_authenticate(user=self.admin_user)
        
        cancel_data = {
            'cancel_at_period_end': True
        }
        
        response = self.client.post(f'/billing/subscriptions/{self.subscription.id}/cancel/', cancel_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'Abonnement annulé' in data['message']
        assert data['cancel_at_period_end'] == True
        
        # Vérifier l'annulation
        self.subscription.refresh_from_db()
        assert self.subscription.canceled_at is not None
        
        print("✅ Subscriptions cancel action")
    
    def test_subscriptions_upgrade_action(self):
        """✅ Test POST /billing/subscriptions/{id}/upgrade/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer un plan supérieur
        premium_plan = Plan.objects.create(
            name="premium",
            display_name="Premium Plan",
            price=Decimal("99.99"),
            billing_interval="monthly",
            included_brands_slots=15,
            included_users_slots=30
        )
        
        upgrade_data = {
            'new_plan_id': premium_plan.id
        }
        
        response = self.client.post(f'/billing/subscriptions/{self.subscription.id}/upgrade/', upgrade_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'mis à jour' in data['message']
        assert data['old_plan'] == 'Test Plan'
        assert data['new_plan'] == 'Premium Plan'
        
        # Vérifier l'upgrade
        self.subscription.refresh_from_db()
        assert self.subscription.plan == premium_plan
        assert self.subscription.amount == premium_plan.price
        
        print("✅ Subscriptions upgrade action")
    
    def test_subscriptions_billing_summary_action(self):
        """✅ Test GET /billing/subscriptions/{id}/billing-summary/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/billing/subscriptions/{self.subscription.id}/billing-summary/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'company' in data
        assert 'plan' in data
        assert 'status' in data
        
        print("✅ Subscriptions billing summary action")
    
    def test_subscriptions_overview_action_superuser_only(self):
        """✅ Test GET /billing/subscriptions/overview/ - Superuser seulement"""
        # Test avec admin normal (doit échouer)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/billing/subscriptions/overview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Créer superuser et tester
        superuser = CustomUser.objects.create_user(
            username='superuser',
            email='super@test.com',
            password='testpass123',
            is_superuser=True
        )
        
        self.client.force_authenticate(user=superuser)
        response = self.client.get('/billing/subscriptions/overview/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_fields = [
            'total_subscriptions', 'active_subscriptions', 'trial_subscriptions',
            'activation_rate', 'revenue', 'subscriptions_by_plan', 'subscriptions_by_status'
        ]
        for field in expected_fields:
            assert field in data
        
        print("✅ Subscriptions overview action superuser only")
    
    def test_subscriptions_permissions_isolation(self):
        """✅ Test isolation des permissions entre companies"""
        # Créer autre company avec subscription
        other_admin = CustomUser.objects.create_user(
            username='other_admin',
            email='other@test.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        other_company = Company.objects.create(
            name="Other Company",
            admin=other_admin,
            billing_email="other@test.com"
        )
        
        other_subscription = Subscription.objects.create(
            company=other_company,
            plan=self.plan,
            status="active",
            started_at=timezone.now(),
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30),
            amount=self.plan.price
        )
        
        # Admin ne doit voir que sa subscription
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/billing/subscriptions/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['company_name'] == 'Subscription Test Company'
        
        # Ne doit pas pouvoir accéder à l'autre subscription
        response = self.client.get(f'/billing/subscriptions/{other_subscription.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        print("✅ Subscriptions permissions isolation")


class InvoiceEndpointsTestCase(APITestCase):
    """Tests des endpoints Invoice"""
    
    def setUp(self):
        """Setup pour tous les tests invoices"""
        self.admin_user = CustomUser.objects.create_user(
            username='invoice_admin',
            email='admin@invoice.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="Invoice Test Company",
            admin=self.admin_user,
            billing_email="billing@invoice.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer plan et subscription
        self.plan = Plan.objects.create(
            name="invoice_plan",
            display_name="Invoice Plan",
            price=Decimal("59.99"),
            billing_interval="monthly"
        )
        
        self.subscription = Subscription.objects.create(
            company=self.company,
            plan=self.plan,
            status="active",
            started_at=timezone.now(),
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30),
            amount=self.plan.price
        )
        
        # Créer invoice
        self.invoice = Invoice.objects.create(
            company=self.company,
            subscription=self.subscription,
            invoice_number="INV-2024-001",
            status="open",
            subtotal=Decimal("59.99"),
            tax_amount=Decimal("11.99"),
            total=Decimal("71.98"),
            invoice_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=15),
            period_start=timezone.now(),
            period_end=timezone.now() + timedelta(days=30)
        )
        
        # Créer invoice items
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Invoice Plan - Mensuel",
            quantity=1,
            unit_price=Decimal("59.99"),
            item_type="plan"
        )
        
        self.client = APIClient()
    
    def test_invoices_list_endpoint(self):
        """✅ Test GET /billing/invoices/ - Liste des factures"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/billing/invoices/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1
        
        # Vérifier les champs du serializer list
        invoice_data = data['results'][0]
        expected_fields = [
            'id', 'company_name', 'invoice_number', 'status', 'total',
            'invoice_date', 'due_date', 'paid_at', 'is_overdue_status'
        ]
        for field in expected_fields:
            assert field in invoice_data
        
        assert invoice_data['company_name'] == 'Invoice Test Company'
        assert invoice_data['invoice_number'] == 'INV-2024-001'
        
        print("✅ Invoices list endpoint")
    
    def test_invoices_detail_endpoint(self):
        """✅ Test GET /billing/invoices/{id}/ - Détail facture"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/billing/invoices/{self.invoice.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['invoice_number'] == 'INV-2024-001'
        assert data['company_name'] == 'Invoice Test Company'
        assert data['plan_name'] == 'Invoice Plan'
        assert data['status'] == 'open'
        assert data['total'] == '71.98'
        assert 'is_overdue_status' in data
        assert 'days_overdue' in data
        assert 'items_list' in data
        
        # Vérifier items_list
        assert len(data['items_list']) == 1
        assert data['items_list'][0]['description'] == 'Invoice Plan - Mensuel'
        
        print("✅ Invoices detail endpoint")
    
    def test_invoices_mark_paid_action(self):
        """✅ Test POST /billing/invoices/{id}/mark-paid/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(f'/billing/invoices/{self.invoice.id}/mark-paid/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'payée' in data['message']
        assert data['invoice_number'] == 'INV-2024-001'
        assert 'paid_at' in data
        
        # Vérifier le changement de statut
        self.invoice.refresh_from_db()
        assert self.invoice.status == 'paid'
        assert self.invoice.paid_at is not None
        
        # Test double paiement (doit échouer)
        response = self.client.post(f'/billing/invoices/{self.invoice.id}/mark-paid/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        print("✅ Invoices mark paid action")
    
    def test_invoices_overdue_action(self):
        """✅ Test GET /billing/invoices/overdue/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer une facture en retard
        overdue_invoice = Invoice.objects.create(
            company=self.company,
            subscription=self.subscription,
            invoice_number="INV-OVERDUE-001",
            status="open",
            subtotal=Decimal("59.99"),
            total=Decimal("59.99"),
            invoice_date=timezone.now() - timedelta(days=45),
            due_date=timezone.now() - timedelta(days=15),  # En retard
            period_start=timezone.now() - timedelta(days=30),
            period_end=timezone.now()
        )
        
        response = self.client.get('/billing/invoices/overdue/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['overdue_count'] == 1
        assert len(data['overdue_invoices']) == 1
        assert data['overdue_invoices'][0]['invoice_number'] == 'INV-OVERDUE-001'
        
        print("✅ Invoices overdue action")
    
    def test_invoices_revenue_stats_action_superuser_only(self):
        """✅ Test GET /billing/invoices/revenue-stats/ - Superuser seulement"""
        # Test avec admin normal (doit échouer)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/billing/invoices/revenue-stats/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Créer superuser et tester
        superuser = CustomUser.objects.create_user(
            username='superuser',
            email='super@test.com',
            password='testpass123',
            is_superuser=True
        )
        
        self.client.force_authenticate(user=superuser)
        response = self.client.get('/billing/invoices/revenue-stats/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_fields = ['revenue_by_status', 'revenue_by_month']
        for field in expected_fields:
            assert field in data
        
        print("✅ Invoices revenue stats action superuser only")
    
    def test_invoices_read_only_viewset(self):
        """✅ Test que InvoiceViewSet est en lecture seule"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test création interdite
        invoice_data = {
            'company': self.company.id,
            'subscription': self.subscription.id,
            'invoice_number': 'FORBIDDEN',
            'status': 'open',
            'total': '100.00'
        }
        
        response = self.client.post('/billing/invoices/', invoice_data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # Test mise à jour interdite (sauf mark-paid)
        response = self.client.patch(f'/billing/invoices/{self.invoice.id}/', {'status': 'paid'})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        print("✅ Invoices read only viewset")


class UsageAlertEndpointsTestCase(APITestCase):
    """Tests des endpoints UsageAlert"""
    
    def setUp(self):
        """Setup pour tous les tests alerts"""
        self.admin_user = CustomUser.objects.create_user(
            username='alert_admin',
            email='admin@alert.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="Alert Test Company",
            admin=self.admin_user,
            billing_email="billing@alert.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer alert
        self.alert = UsageAlert.objects.create(
            company=self.company,
            alert_type="brands_warning",
            status="active",
            message="Vous approchez de la limite de marques (4/5)"
        )
        
        self.client = APIClient()
    
    def test_usage_alerts_list_endpoint(self):
        """✅ Test GET /billing/alerts/ - Liste des alertes"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/billing/alerts/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1
        
        alert_data = data['results'][0]
        expected_fields = [
            'id', 'company', 'company_name', 'alert_type', 'status',
            'message', 'triggered_at', 'resolved_at'
        ]
        for field in expected_fields:
            assert field in alert_data
        
        assert alert_data['company_name'] == 'Alert Test Company'
        assert alert_data['alert_type'] == 'brands_warning'
        
        print("✅ Usage alerts list endpoint")
    
    def test_usage_alerts_resolve_action(self):
        """✅ Test POST /billing/alerts/{id}/resolve/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(f'/billing/alerts/{self.alert.id}/resolve/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'résolue' in data['message']
        assert 'resolved_at' in data
        
        # Vérifier la résolution
        self.alert.refresh_from_db()
        assert self.alert.status == 'resolved'
        assert self.alert.resolved_at is not None
        
        # Test double résolution (doit échouer)
        response = self.client.post(f'/billing/alerts/{self.alert.id}/resolve/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        print("✅ Usage alerts resolve action")
    
    def test_usage_alerts_dismiss_action(self):
        """✅ Test POST /billing/alerts/{id}/dismiss/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer nouvelle alert pour ce test
        alert = UsageAlert.objects.create(
            company=self.company,
            alert_type="users_warning",
            status="active",
            message="Test dismiss"
        )
        
        response = self.client.post(f'/billing/alerts/{alert.id}/dismiss/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'ignorée' in data['message']
        
        # Vérifier le dismiss
        alert.refresh_from_db()
        assert alert.status == 'dismissed'
        assert alert.resolved_at is not None
        
        print("✅ Usage alerts dismiss action")
    
    def test_usage_alerts_active_alerts_action(self):
        """✅ Test GET /billing/alerts/active-alerts/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer plusieurs types d'alertes
        UsageAlert.objects.create(
            company=self.company,
            alert_type="users_limit",
            status="active",
            message="Limite utilisateurs atteinte"
        )
        
        response = self.client.get('/billing/alerts/active-alerts/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['active_alerts_count'] == 2  # alert existante + nouvelle
        assert 'alerts_by_type' in data
        assert 'Avertissement brands (80%)' in data['alerts_by_type']
        assert 'Limite utilisateurs atteinte' in data['alerts_by_type']
        
        print("✅ Usage alerts active alerts action")
    
    def test_usage_alerts_permissions_isolation(self):
        """✅ Test isolation des permissions entre companies"""
        # Créer autre company avec alert
        other_company = Company.objects.create(
            name="Other Alert Company",
            admin=self.admin_user,  # Simplification
            billing_email="other@alert.com"
        )
        
        other_alert = UsageAlert.objects.create(
            company=other_company,
            alert_type="brands_limit",
            status="active",
            message="Other company alert"
        )
        
        # Admin ne doit voir que ses alerts
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/billing/alerts/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['company_name'] == 'Alert Test Company'
        
        print("✅ Usage alerts permissions isolation")

print("📁 Tests endpoints Billing créés avec succès !")
print("🔧 Commandes pour exécuter :")
print("   pytest tests/test_billing_endpoints.py -v")
print("   pytest tests/test_billing_endpoints.py::PlanEndpointsTestCase -v")
print("   pytest tests/test_billing_endpoints.py::SubscriptionEndpointsTestCase -v")
print("   pytest tests/test_billing_endpoints.py::InvoiceEndpointsTestCase -v")