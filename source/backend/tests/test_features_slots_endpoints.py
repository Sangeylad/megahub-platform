# backend/tests/test_features_slots_endpoints.py

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
from brands_core.models.brand import Brand
from company_slots.models.slots import CompanySlots
from company_features.models.features import Feature, CompanyFeature, FeatureUsageLog

User = get_user_model()

class FeatureEndpointsTestCase(APITestCase):
    """Tests des endpoints Feature"""
    
    def setUp(self):
        """Setup pour tous les tests features"""
        # Créer superuser pour certains tests admin
        self.superuser = CustomUser.objects.create_user(
            username='feature_super',
            email='super@feature.com',
            password='testpass123',
            is_superuser=True
        )
        
        # Créer admin
        self.admin_user = CustomUser.objects.create_user(
            username='feature_admin',
            email='admin@feature.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        # Créer company
        self.company = Company.objects.create(
            name="Feature Test Company",
            admin=self.admin_user,
            billing_email="billing@feature.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer features
        self.websites_feature = Feature.objects.create(
            name="websites_management",
            display_name="Gestion des Sites Web",
            description="Création et gestion de sites web",
            feature_type="websites",
            is_active=True,
            is_premium=False,
            sort_order=1
        )
        
        self.ai_feature = Feature.objects.create(
            name="ai_templates",
            display_name="Templates IA",
            description="Génération de contenu avec IA",
            feature_type="templates",
            is_active=True,
            is_premium=True,
            sort_order=2
        )
        
        self.client = APIClient()
    
    def test_features_list_endpoint(self):
        """✅ Test GET /features/available/ - Liste des features"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/features/available/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 2
        
        # Vérifier les champs du serializer
        feature_data = data['results'][0]
        expected_fields = [
            'id', 'name', 'display_name', 'description', 'feature_type',
            'is_active', 'is_premium', 'sort_order', 'subscribed_companies_count'
        ]
        for field in expected_fields:
            assert field in feature_data
        
        # Vérifier l'ordre de tri
        assert data['results'][0]['sort_order'] <= data['results'][1]['sort_order']
        
        print("✅ Features list endpoint")
    
    def test_features_detail_endpoint(self):
        """✅ Test GET /features/available/{id}/ - Détail feature"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/features/available/{self.websites_feature.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['name'] == 'websites_management'
        assert data['display_name'] == 'Gestion des Sites Web'
        assert data['feature_type'] == 'websites'
        assert data['is_premium'] == False
        assert 'subscribed_companies_count' in data
        
        print("✅ Features detail endpoint")
    
    def test_features_admin_only_crud(self):
        """✅ Test CRUD features - Admin seulement"""
        # Test création avec utilisateur normal (doit échouer)
        self.client.force_authenticate(user=self.admin_user)
        
        feature_data = {
            'name': 'forbidden_feature',
            'display_name': 'Forbidden Feature',
            'description': 'Should not be created',
            'feature_type': 'other'
        }
        
        response = self.client.post('/features/available/', feature_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test avec superuser (doit réussir)
        self.client.force_authenticate(user=self.superuser)
        
        response = self.client.post('/features/available/', feature_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Vérifier création
        assert Feature.objects.filter(name='forbidden_feature').exists()
        
        # Test mise à jour avec superuser
        new_feature = Feature.objects.get(name='forbidden_feature')
        update_data = {'description': 'Updated description'}
        
        response = self.client.patch(f'/features/available/{new_feature.id}/', update_data)
        assert response.status_code == status.HTTP_200_OK
        
        print("✅ Features admin only CRUD")
    
    def test_features_filtering(self):
        """✅ Test filtrage des features"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Filtrer par type
        response = self.client.get('/features/available/?feature_type=websites')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['feature_type'] == 'websites'
        
        # Filtrer par premium
        response = self.client.get('/features/available/?is_premium=true')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['is_premium'] == True
        
        print("✅ Features filtering")


class CompanyFeatureEndpointsTestCase(APITestCase):
    """Tests des endpoints CompanyFeature"""
    
    def setUp(self):
        """Setup pour tous les tests company features"""
        self.admin_user = CustomUser.objects.create_user(
            username='cf_admin',
            email='admin@cf.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="CompanyFeature Test Company",
            admin=self.admin_user,
            billing_email="billing@cf.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer brand et user
        self.brand_user = CustomUser.objects.create_user(
            username='cf_user',
            email='user@cf.com',
            password='testpass123',
            company=self.company,
            user_type='brand_member'
        )
        
        self.brand = Brand.objects.create(
            company=self.company,
            name="CF Brand",
            brand_admin=self.brand_user
        )
        
        # Créer features
        self.websites_feature = Feature.objects.create(
            name="cf_websites",
            display_name="CF Websites",
            feature_type="websites",
            is_active=True
        )
        
        self.premium_feature = Feature.objects.create(
            name="cf_premium",
            display_name="CF Premium",
            feature_type="analytics",
            is_active=True,
            is_premium=True
        )
        
        # Créer company features
        self.company_feature = CompanyFeature.objects.create(
            company=self.company,
            feature=self.websites_feature,
            is_enabled=True,
            usage_limit=100,
            current_usage=25
        )
        
        self.premium_company_feature = CompanyFeature.objects.create(
            company=self.company,
            feature=self.premium_feature,
            is_enabled=True,
            usage_limit=50,
            current_usage=45,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        self.client = APIClient()
    
    def test_company_features_list_endpoint(self):
        """✅ Test GET /features/subscriptions/ - Liste des features company"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/features/subscriptions/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 2
        
        # Vérifier les champs du serializer list
        cf_data = data['results'][0]
        expected_fields = [
            'id', 'feature', 'feature_name', 'feature_type',
            'is_enabled', 'is_active_status', 'usage_info', 'expires_at'
        ]
        for field in expected_fields:
            assert field in cf_data
        
        # Vérifier usage_info
        assert 'unlimited' in cf_data['usage_info']
        if not cf_data['usage_info']['unlimited']:
            assert 'current' in cf_data['usage_info']
            assert 'limit' in cf_data['usage_info']
            assert 'percentage' in cf_data['usage_info']
        
        print("✅ Company features list endpoint")
    
    def test_company_features_detail_endpoint(self):
        """✅ Test GET /features/subscriptions/{id}/ - Détail company feature"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/features/subscriptions/{self.company_feature.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['feature_name'] == 'CF Websites'
        assert data['company_name'] == 'CompanyFeature Test Company'
        assert data['usage_limit'] == 100
        assert data['current_usage'] == 25
        assert 'usage_percentage' in data
        assert 'is_usage_limit_reached_status' in data
        assert 'days_until_expiry' in data
        
        print("✅ Company features detail endpoint")
    
    def test_company_features_create_endpoint(self):
        """✅ Test POST /features/subscriptions/ - Création company feature"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer nouvelle feature
        new_feature = Feature.objects.create(
            name="cf_new",
            display_name="CF New Feature",
            feature_type="crm"
        )
        
        cf_data = {
            'company': self.company.id,
            'feature': new_feature.id,
            'is_enabled': True,
            'usage_limit': 200,
            'expires_at': (timezone.now() + timedelta(days=365)).isoformat()
        }
        
        response = self.client.post('/features/subscriptions/', cf_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Vérifier création
        assert CompanyFeature.objects.filter(company=self.company, feature=new_feature).exists()
        
        print("✅ Company features create endpoint")
    
    def test_company_features_create_duplicate_error(self):
        """✅ Test POST /features/subscriptions/ - Erreur de duplication"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Essayer de créer un doublon
        cf_data = {
            'company': self.company.id,
            'feature': self.websites_feature.id,  # Déjà existant
            'is_enabled': True
        }
        
        response = self.client.post('/features/subscriptions/', cf_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'déjà abonnée' in str(response.json())
        
        print("✅ Company features create duplicate error")
    
    def test_company_features_update_endpoint(self):
        """✅ Test PUT/PATCH /features/subscriptions/{id}/ - Mise à jour"""
        self.client.force_authenticate(user=self.admin_user)
        
        update_data = {
            'usage_limit': 150,
            'is_enabled': False
        }
        
        response = self.client.patch(f'/features/subscriptions/{self.company_feature.id}/', update_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier mise à jour
        self.company_feature.refresh_from_db()
        assert self.company_feature.usage_limit == 150
        assert self.company_feature.is_enabled == False
        
        print("✅ Company features update endpoint")
    
    def test_company_features_increment_usage_action(self):
        """✅ Test POST /features/subscriptions/{id}/increment-usage/"""
        self.client.force_authenticate(user=self.admin_user)
        
        increment_data = {'amount': 5}
        
        response = self.client.post(f'/features/subscriptions/{self.company_feature.id}/increment-usage/', increment_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['current_usage'] == 30  # 25 + 5
        assert 'usage_percentage' in data
        assert 'limit_reached' in data
        
        # Vérifier l'incrémentation
        self.company_feature.refresh_from_db()
        assert self.company_feature.current_usage == 30
        
        print("✅ Company features increment usage action")
    
    def test_company_features_increment_usage_limit_error(self):
        """✅ Test POST /features/subscriptions/{id}/increment-usage/ - Erreur limite"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Essayer d'incrémenter au-delà de la limite
        increment_data = {'amount': 100}  # 25 + 100 = 125 > 100 (limite)
        
        response = self.client.post(f'/features/subscriptions/{self.company_feature.id}/increment-usage/', increment_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Limite d\'utilisation' in str(response.json())
        
        print("✅ Company features increment usage limit error")
    
    def test_company_features_reset_usage_action(self):
        """✅ Test POST /features/subscriptions/{id}/reset-usage/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(f'/features/subscriptions/{self.company_feature.id}/reset-usage/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['old_usage'] == 25
        assert data['current_usage'] == 0
        
        # Vérifier le reset
        self.company_feature.refresh_from_db()
        assert self.company_feature.current_usage == 0
        
        print("✅ Company features reset usage action")
    
    def test_company_features_toggle_enabled_action(self):
        """✅ Test POST /features/subscriptions/{id}/toggle-enabled/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Feature activée initialement
        assert self.company_feature.is_enabled == True
        
        response = self.client.post(f'/features/subscriptions/{self.company_feature.id}/toggle-enabled/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'désactivée' in data['message']
        assert data['is_enabled'] == False
        
        # Vérifier le toggle
        self.company_feature.refresh_from_db()
        assert self.company_feature.is_enabled == False
        
        print("✅ Company features toggle enabled action")
    
    def test_company_features_by_company_action(self):
        """✅ Test GET /features/subscriptions/by-company/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/features/subscriptions/by-company/?company_id={self.company.id}')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'features_by_type' in data
        assert 'websites' in data['features_by_type']
        assert 'analytics' in data['features_by_type']
        assert data['total_features'] == 2
        assert data['active_features'] == 2
        
        print("✅ Company features by company action")
    
    def test_company_features_usage_stats_action(self):
        """✅ Test GET /features/subscriptions/usage-stats/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/features/subscriptions/usage-stats/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'global_stats' in data
        assert 'stats_by_type' in data
        
        # Vérifier global_stats
        assert 'total_features' in data['global_stats']
        assert 'active_features' in data['global_stats']
        assert 'over_limit_features' in data['global_stats']
        assert 'activation_rate' in data['global_stats']
        
        print("✅ Company features usage stats action")
    
    def test_company_features_permissions_isolation(self):
        """✅ Test isolation des permissions entre companies"""
        # Créer autre company avec features
        other_company = Company.objects.create(
            name="Other CF Company",
            admin=self.admin_user,  # Simplification
            billing_email="other@cf.com"
        )
        
        other_cf = CompanyFeature.objects.create(
            company=other_company,
            feature=self.websites_feature,
            is_enabled=True
        )
        
        # Admin ne doit voir que ses company features
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/features/subscriptions/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 2  # Seulement les features de sa company
        
        # Ne doit pas pouvoir accéder à l'autre company feature
        response = self.client.get(f'/features/subscriptions/{other_cf.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        print("✅ Company features permissions isolation")


class CompanySlotsEndpointsTestCase(APITestCase):
    """Tests des endpoints CompanySlots"""
    
    def setUp(self):
        """Setup pour tous les tests slots"""
        # Créer superuser
        self.superuser = CustomUser.objects.create_user(
            username='slots_super',
            email='super@slots.com',
            password='testpass123',
            is_superuser=True
        )
        
        # Créer admin
        self.admin_user = CustomUser.objects.create_user(
            username='slots_admin',
            email='admin@slots.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        # Créer company
        self.company = Company.objects.create(
            name="Slots Test Company",
            admin=self.admin_user,
            billing_email="billing@slots.com"
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
        
        # Créer quelques brands et users pour les compteurs
        Brand.objects.create(company=self.company, name="Slot Brand 1")
        Brand.objects.create(company=self.company, name="Slot Brand 2")
        
        CustomUser.objects.create_user(
            username='slot_user1',
            email='user1@slots.com',
            password='testpass123',
            company=self.company
        )
        CustomUser.objects.create_user(
            username='slot_user2',
            email='user2@slots.com',
            password='testpass123',
            company=self.company
        )
        
        self.client = APIClient()
    
    def test_company_slots_list_endpoint(self):
        """✅ Test GET /company-slots/ - Liste des slots"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/company-slots/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1  # Ses propres slots
        
        # Vérifier les champs du serializer
        slots_data = data['results'][0]
        expected_fields = [
            'id', 'company', 'company_name', 'brands_slots', 'users_slots',
            'current_brands_count', 'current_users_count',
            'brands_usage_percentage', 'users_usage_percentage',
            'available_brands_slots', 'available_users_slots',
            'is_brands_limit_reached', 'is_users_limit_reached'
        ]
        for field in expected_fields:
            assert field in slots_data
        
        assert slots_data['company_name'] == 'Slots Test Company'
        assert slots_data['brands_slots'] == 5
        assert slots_data['users_slots'] == 10
        
        print("✅ Company slots list endpoint")
    
    def test_company_slots_detail_endpoint(self):
        """✅ Test GET /company-slots/{id}/ - Détail slots"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/company-slots/{self.slots.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['brands_slots'] == 5
        assert data['users_slots'] == 10
        assert data['current_brands_count'] == 2
        assert data['current_users_count'] == 3
        assert 'brands_usage_percentage' in data
        assert 'users_usage_percentage' in data
        
        # Vérifier les calculs
        assert data['brands_usage_percentage'] == 40.0  # 2/5 * 100
        assert data['users_usage_percentage'] == 30.0   # 3/10 * 100
        
        print("✅ Company slots detail endpoint")
    
    def test_company_slots_update_endpoint(self):
        """✅ Test PUT/PATCH /company-slots/{id}/ - Mise à jour slots"""
        self.client.force_authenticate(user=self.admin_user)
        
        update_data = {
            'brands_slots': 8,
            'users_slots': 15
        }
        
        response = self.client.patch(f'/company-slots/{self.slots.id}/', update_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier mise à jour
        self.slots.refresh_from_db()
        assert self.slots.brands_slots == 8
        assert self.slots.users_slots == 15
        
        print("✅ Company slots update endpoint")
    
    def test_company_slots_update_validation_error(self):
        """✅ Test PUT/PATCH /company-slots/{id}/ - Erreur validation"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Essayer de réduire en-dessous de l'usage actuel
        update_data = {
            'brands_slots': 1,  # Actuel: 2, impossible
            'users_slots': 2    # Actuel: 3, impossible
        }
        
        response = self.client.patch(f'/company-slots/{self.slots.id}/', update_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        errors = response.json()
        assert 'brands_slots' in errors
        assert 'users_slots' in errors
        assert '2 brands sont actuellement utilisées' in str(errors)
        
        print("✅ Company slots update validation error")
    
    def test_company_slots_refresh_counts_action(self):
        """✅ Test POST /company-slots/{id}/refresh-counts/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(f'/company-slots/{self.slots.id}/refresh-counts/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'mis à jour' in data['message']
        assert 'slots' in data
        
        # Les compteurs devraient être mis à jour automatiquement
        self.slots.refresh_from_db()
        # Note: Les compteurs peuvent être différents selon les créations pendant le test
        
        print("✅ Company slots refresh counts action")
    
    def test_company_slots_usage_alerts_action(self):
        """✅ Test GET /company-slots/{id}/usage-alerts/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Modifier les slots pour créer des alertes
        self.slots.current_brands_count = 5  # 100% d'utilisation
        self.slots.current_users_count = 9   # 90% d'utilisation
        self.slots.save()
        
        response = self.client.get(f'/company-slots/{self.slots.id}/usage-alerts/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'company' in data
        assert 'alerts_count' in data
        assert 'alerts' in data
        
        # Devrait avoir des alertes vu les pourcentages élevés
        assert data['alerts_count'] >= 1
        
        print("✅ Company slots usage alerts action")
    
    def test_company_slots_increase_slots_action(self):
        """✅ Test POST /company-slots/{id}/increase-slots/"""
        self.client.force_authenticate(user=self.admin_user)
        
        increase_data = {
            'brands_increment': 3,
            'users_increment': 5
        }
        
        response = self.client.post(f'/company-slots/{self.slots.id}/increase-slots/', increase_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'augmentés' in data['message']
        assert data['changes']['brands_slots']['old'] == 5
        assert data['changes']['brands_slots']['new'] == 8
        assert data['changes']['users_slots']['old'] == 10
        assert data['changes']['users_slots']['new'] == 15
        
        # Vérifier l'augmentation
        self.slots.refresh_from_db()
        assert self.slots.brands_slots == 8
        assert self.slots.users_slots == 15
        
        print("✅ Company slots increase slots action")
    
    def test_company_slots_increase_slots_validation_errors(self):
        """✅ Test POST /company-slots/{id}/increase-slots/ - Erreurs validation"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test incréments négatifs
        increase_data = {
            'brands_increment': -1,
            'users_increment': 5
        }
        
        response = self.client.post(f'/company-slots/{self.slots.id}/increase-slots/', increase_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'positifs' in str(response.json())
        
        # Test aucun incrément
        increase_data = {
            'brands_increment': 0,
            'users_increment': 0
        }
        
        response = self.client.post(f'/company-slots/{self.slots.id}/increase-slots/', increase_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'incrément doit être spécifié' in str(response.json())
        
        print("✅ Company slots increase slots validation errors")
    
    def test_company_slots_overview_action_superuser_only(self):
        """✅ Test GET /company-slots/overview/ - Superuser seulement"""
        # Test avec admin normal (doit échouer)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/company-slots/overview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test avec superuser
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/company-slots/overview/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_fields = [
            'total_slots', 'total_used', 'usage_percentages',
            'companies_near_limit', 'companies_count'
        ]
        for field in expected_fields:
            assert field in data
        
        assert 'brands' in data['total_slots']
        assert 'users' in data['total_slots']
        
        print("✅ Company slots overview action superuser only")
    
    def test_company_slots_permissions_isolation(self):
        """✅ Test isolation des permissions entre companies"""
        # Créer autre company avec slots
        other_company = Company.objects.create(
            name="Other Slots Company",
            admin=self.admin_user,  # Simplification
            billing_email="other@slots.com"
        )
        
        other_slots = CompanySlots.objects.create(
            company=other_company,
            brands_slots=3,
            users_slots=8
        )
        
        # Admin ne doit voir que ses slots
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/company-slots/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['company_name'] == 'Slots Test Company'
        
        # Ne doit pas pouvoir accéder aux autres slots
        response = self.client.get(f'/company-slots/{other_slots.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        print("✅ Company slots permissions isolation")


class FeaturesAdvancedEndpointsTestCase(APITestCase):
    """Tests avancés des endpoints Features"""
    
    def setUp(self):
        """Setup pour tests avancés"""
        self.superuser = CustomUser.objects.create_user(
            username='advanced_super',
            email='super@advanced.com',
            password='testpass123',
            is_superuser=True
        )
        
        self.admin_user = CustomUser.objects.create_user(
            username='advanced_admin',
            email='admin@advanced.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="Advanced Test Company",
            admin=self.admin_user,
            billing_email="billing@advanced.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        self.client = APIClient()
    
    def test_company_features_companies_overview_superuser_only(self):
        """✅ Test GET /features/subscriptions/companies-overview/ - Superuser seulement"""
        # Test avec admin normal (doit échouer)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/features/subscriptions/companies-overview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test avec superuser
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/features/subscriptions/companies-overview/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'companies_count' in data
        assert 'companies' in data
        
        print("✅ Company features companies overview superuser only")
    
    def test_feature_usage_log_creation(self):
        """✅ Test création de logs d'utilisation"""
        # Créer feature et company feature
        feature = Feature.objects.create(
            name="log_feature",
            display_name="Log Feature",
            feature_type="websites"
        )
        
        company_feature = CompanyFeature.objects.create(
            company=self.company,
            feature=feature,
            is_enabled=True,
            usage_limit=10,
            current_usage=0
        )
        
        # Créer brand et user
        brand = Brand.objects.create(company=self.company, name="Log Brand")
        
        brand_user = CustomUser.objects.create_user(
            username='log_user',
            email='log@test.com',
            password='testpass123',
            company=self.company
        )
        
        # Créer log d'utilisation
        usage_log = FeatureUsageLog.objects.create(
            company_feature=company_feature,
            action="website_created",
            quantity=1,
            user=brand_user,
            brand=brand,
            metadata={"website_id": 123, "template": "business"}
        )
        
        # Vérifier le log
        assert usage_log.company_feature == company_feature
        assert usage_log.action == "website_created"
        assert usage_log.user == brand_user
        assert usage_log.brand == brand
        assert usage_log.metadata["website_id"] == 123
        
        print("✅ Feature usage log creation")
    
    def test_company_feature_expiration_logic(self):
        """✅ Test logique d'expiration des features"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer feature qui expire bientôt
        feature = Feature.objects.create(
            name="expiring_feature",
            display_name="Expiring Feature",
            feature_type="premium"
        )
        
        # Feature qui expire dans 1 jour
        expiring_cf = CompanyFeature.objects.create(
            company=self.company,
            feature=feature,
            is_enabled=True,
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # Test que la feature est encore active
        response = self.client.get(f'/features/subscriptions/{expiring_cf.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['is_active_status'] == True
        assert data['days_until_expiry'] == 1
        
        # Simuler expiration (modifier en backend)
        expiring_cf.expires_at = timezone.now() - timedelta(days=1)
        expiring_cf.save()
        
        # Test que la feature est maintenant inactive
        response = self.client.get(f'/features/subscriptions/{expiring_cf.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['is_active_status'] == False
        assert data['days_until_expiry'] == 0
        
        print("✅ Company feature expiration logic")

print("📁 Tests endpoints Features/Slots créés avec succès !")
print("🔧 Commandes pour exécuter :")
print("   pytest tests/test_features_slots_endpoints.py -v")
print("   pytest tests/test_features_slots_endpoints.py::FeatureEndpointsTestCase -v")
print("   pytest tests/test_features_slots_endpoints.py::CompanyFeatureEndpointsTestCase -v")
print("   pytest tests/test_features_slots_endpoints.py::CompanySlotsEndpointsTestCase -v")