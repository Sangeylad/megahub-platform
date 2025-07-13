# backend/onboarding_business/tests/test_business_endpoints.py
"""
Tests des endpoints du système onboarding business
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from .factories import (
    UserFactory, CompanyFactory, BrandFactory, 
    CompanySlotsFactory, CompanyFeatureFactory
)

User = get_user_model()

class OnboardingBusinessSetupStatusEndpointTest(APITestCase):
    """Tests de l'endpoint setup-status"""
    
    def setUp(self):
        """Setup commun pour tous les tests"""
        self.url = reverse('onboarding_business:setup_status')
    
    def test_setup_status_requires_authentication(self):
        """
        Test que l'endpoint setup-status requiert authentication
        
        Given: Aucune authentication
        When: GET /onboarding/business/setup-status/
        Then: 401 Unauthorized
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_setup_status_user_without_company_returns_no_business(self):
        """
        Test setup status pour user sans company
        
        Given: User authentifié sans company
        When: GET setup-status
        Then: has_business = False
        """
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['data']['has_business'])
    
    def test_setup_status_user_with_company_returns_business_summary(self):
        """
        Test setup status pour user avec company
        
        Given: User avec company + brand
        When: GET setup-status  
        Then: has_business = True avec résumé complet
        """
        company = CompanyFactory()
        user = UserFactory(company=company, user_type='agency_admin')
        brand = BrandFactory(company=company, brand_admin=user)
        brand.users.add(user)
        
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Vérifications structure réponse
        self.assertTrue(data['has_business'])
        self.assertIn('company', data)
        self.assertIn('brands', data)
        self.assertIn('permissions', data)
        
        # Vérifications company
        self.assertEqual(data['company']['id'], company.id)
        self.assertEqual(data['company']['name'], company.name)
        
        # Vérifications brands
        self.assertEqual(len(data['brands']), 1)
        self.assertEqual(data['brands'][0]['id'], brand.id)
        self.assertTrue(data['brands'][0]['is_admin'])
    
    def test_setup_status_user_with_trial_shows_trial_info(self):
        """
        Test setup status avec trial actif
        
        Given: User avec company en trial
        When: GET setup-status
        Then: Infos trial présentes
        """
        trial_end = timezone.now() + timedelta(weeks=1)
        company = CompanyFactory(trial_expires_at=trial_end)
        user = UserFactory(company=company, user_type='agency_admin')
        
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company_data = response.data['data']['company']
        
        self.assertTrue(company_data['is_trial'])
        self.assertGreater(company_data['trial_days_remaining'], 0)
    
    @patch('onboarding_business.services.business_creation.get_business_creation_summary')
    def test_setup_status_handles_service_error(self, mock_service):
        """
        Test gestion d'erreur du service
        
        Given: Service lève une exception
        When: GET setup-status
        Then: 500 avec message d'erreur
        """
        mock_service.side_effect = Exception("Service error")
        
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

class OnboardingBusinessStatsEndpointTest(APITestCase):
    """Tests de l'endpoint business-stats"""
    
    def setUp(self):
        """Setup commun"""
        self.url = reverse('onboarding_business:business_stats')
        
        # User avec company complète
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, user_type='agency_admin')
        self.brand = BrandFactory(company=self.company, brand_admin=self.user)
        self.brand.users.add(self.user)
        
        # Slots
        self.slots = CompanySlotsFactory(company=self.company)
        
        self.client.force_authenticate(user=self.user)
    
    def test_business_stats_requires_authentication(self):
        """
        Test authentication requise
        
        Given: Pas d'authentication
        When: GET business-stats
        Then: 401
        """
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_business_stats_user_without_company_returns_404(self):
        """
        Test user sans company
        
        Given: User sans company
        When: GET business-stats
        Then: 404
        """
        user_no_company = UserFactory()
        self.client.force_authenticate(user=user_no_company)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User sans company', response.data['error'])
    
    def test_business_stats_returns_complete_data(self):
        """
        Test retour stats complètes
        
        Given: User avec company complète
        When: GET business-stats
        Then: Stats complètes retournées
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Vérifier sections présentes
        expected_sections = ['company', 'slots', 'features', 'trial', 'user_roles']
        for section in expected_sections:
            with self.subTest(section=section):
                self.assertIn(section, data)
        
        # Vérifier structure slots
        slots_data = data['slots']
        self.assertIn('brands', slots_data)
        self.assertIn('users', slots_data)
        self.assertIn('current', slots_data['brands'])
        self.assertIn('limit', slots_data['brands'])
        self.assertIn('can_add', slots_data['brands'])
    
    def test_business_stats_with_features(self):
        """
        Test stats avec features
        
        Given: Company avec features activées
        When: GET business-stats
        Then: Features dans les stats
        """
        # Créer des features
        feature1 = CompanyFeatureFactory(company=self.company)
        feature2 = CompanyFeatureFactory(company=self.company, is_enabled=False)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        features_data = response.data['data']['features']
        
        self.assertGreater(features_data['total_features'], 0)
        self.assertIn('active_features', features_data)
    
    def test_business_stats_solo_vs_agency_mode(self):
        """
        Test détection mode solo vs agency
        
        Given: Company avec 1 brand (solo)
        When: GET business-stats
        Then: business_mode = 'solo'
        
        When: Ajouter 2ème brand
        Then: business_mode = 'agency'
        """
        # Test mode solo
        response = self.client.get(self.url)
        company_data = response.data['data']['company']
        self.assertEqual(company_data['business_mode'], 'solo')
        
        # Ajouter 2ème brand
        brand2 = BrandFactory(company=self.company)
        
        response = self.client.get(self.url)
        company_data = response.data['data']['company']
        self.assertEqual(company_data['business_mode'], 'agency')

class OnboardingBusinessFeaturesSummaryEndpointTest(APITestCase):
    """Tests de l'endpoint features-summary"""
    
    def setUp(self):
        """Setup commun"""
        self.url = reverse('onboarding_business:features_summary')
        
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        
        self.client.force_authenticate(user=self.user)
    
    def test_features_summary_requires_authentication(self):
        """Test authentication requise"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_features_summary_user_without_company_returns_404(self):
        """Test user sans company"""
        user_no_company = UserFactory()
        self.client.force_authenticate(user=user_no_company)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_features_summary_empty_features_returns_zero(self):
        """
        Test company sans features
        
        Given: Company sans features activées
        When: GET features-summary
        Then: total_features = 0
        """
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        self.assertEqual(data['total_features'], 0)
        self.assertEqual(len(data['active_features']), 0)
    
    def test_features_summary_with_active_features(self):
        """
        Test company avec features actives
        
        Given: Company avec features activées et désactivées
        When: GET features-summary
        Then: Seules features actives retournées
        """
        # Features activées
        feature1 = CompanyFeatureFactory(company=self.company, is_enabled=True)
        feature2 = CompanyFeatureFactory(company=self.company, is_enabled=True)
        
        # Feature désactivée
        feature3 = CompanyFeatureFactory(company=self.company, is_enabled=False)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Seules features actives
        self.assertEqual(data['total_features'], 2)
        self.assertEqual(len(data['active_features']), 2)
        
        # Vérifier structure feature
        feature_data = data['active_features'][0]
        expected_fields = [
            'name', 'display_name', 'is_premium', 
            'usage_limit', 'current_usage', 'is_active'
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, feature_data)
    
    def test_features_summary_with_expired_features(self):
        """
        Test features expirées
        
        Given: Company avec feature expirée
        When: GET features-summary
        Then: Feature marquée comme inactive
        """
        expired_date = timezone.now() - timedelta(days=1)
        feature = CompanyFeatureFactory(
            company=self.company,
            is_enabled=True,
            expires_at=expired_date
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Feature présente mais inactive
        self.assertEqual(data['total_features'], 1)
        feature_data = data['active_features'][0]
        self.assertFalse(feature_data['is_active'])

class OnboardingBusinessTriggerCreationEndpointTest(APITestCase):
    """Tests de l'endpoint trigger-business-creation (fallback manuel)"""
    
    def setUp(self):
        """Setup commun"""
        self.url = reverse('onboarding_registration:trigger_business_creation')
    
    def test_trigger_creation_requires_authentication(self):
        """Test authentication requise"""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_trigger_creation_user_already_has_company_fails(self):
        """
        Test user avec company existante
        
        Given: User avec company existante
        When: POST trigger-business-creation
        Then: 400 avec erreur
        """
        company = CompanyFactory()
        user = UserFactory(company=company)
        
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non éligible', response.data['error'])
    
    @patch('onboarding_business.services.business_creation.create_solo_business_for_user')
    def test_trigger_creation_success_creates_business(self, mock_create):
        """
        Test création business réussie
        
        Given: User éligible
        When: POST trigger-business-creation
        Then: Business créé avec succès
        """
        user = UserFactory()
        company = CompanyFactory()
        brand = BrandFactory()
        
        # Mock retour service
        mock_create.return_value = {
            'company': company,
            'brand': brand
        }
        
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.url, {
            'business_name': 'Test Business'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # Vérifier appel service
        mock_create.assert_called_once_with(user, business_name='Test Business')
    
    @patch('onboarding_business.services.business_creation.create_solo_business_for_user')
    def test_trigger_creation_service_error_returns_500(self, mock_create):
        """
        Test gestion erreur service
        
        Given: Service lève exception
        When: POST trigger-business-creation
        Then: 500 avec erreur
        """
        mock_create.side_effect = Exception("Creation failed")
        
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
    
    def test_trigger_creation_superuser_not_eligible(self):
        """
        Test superuser non éligible
        
        Given: User superuser
        When: POST trigger-business-creation
        Then: 400 non éligible
        """
        user = UserFactory(is_superuser=True)
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non éligible', response.data['error'])
    
    def test_trigger_creation_staff_user_not_eligible(self):
        """
        Test staff user non éligible
        
        Given: User staff
        When: POST trigger-business-creation  
        Then: 400 non éligible
        """
        user = UserFactory(is_staff=True)
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OnboardingBusinessEndpointsIntegrationTest(APITestCase):
    """Tests d'intégration des endpoints business"""
    
    def test_complete_business_setup_flow(self):
        """
        Test flow complet setup business
        
        Given: User nouvellement créé
        When: Sequence d'appels endpoints
        Then: Business complet configuré
        """
        # 1. User sans business
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        # 2. Trigger création business
        with patch('onboarding_business.services.business_creation.create_solo_business_for_user') as mock_create:
            company = CompanyFactory()
            brand = BrandFactory(company=company)
            
            mock_create.return_value = {
                'company': company,
                'brand': brand
            }
            
            # Simuler mise à jour user
            user.company = company
            user.user_type = 'agency_admin'
            user.save()
            brand.users.add(user)
            
            # Trigger creation
            trigger_url = reverse('onboarding_registration:trigger_business_creation')
            response = self.client.post(trigger_url, {
                'business_name': 'My Business'
            })
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Vérifier setup status
        setup_url = reverse('onboarding_business:setup_status')
        response = self.client.get(setup_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['has_business'])
        
        # 4. Vérifier business stats
        stats_url = reverse('onboarding_business:business_stats')
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('company', response.data['data'])
        
        # 5. Vérifier features summary
        features_url = reverse('onboarding_business:features_summary')
        response = self.client.get(features_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

@pytest.mark.django_db
class OnboardingBusinessEndpointsPerformanceTest(TestCase):
    """Tests de performance des endpoints business"""
    
    def test_setup_status_endpoint_performance(self):
        """
        Test performance setup-status avec données volumineuses
        
        Given: User avec many brands et features
        When: GET setup-status
        Then: Réponse < 500ms
        """
        import time
        
        # Setup données volumineuses
        company = CompanyFactory()
        user = UserFactory(company=company, user_type='agency_admin')
        
        # Créer plusieurs brands
        brands = [BrandFactory(company=company) for _ in range(10)]
        for brand in brands:
            brand.users.add(user)
        
        # Créer plusieurs features
        features = [CompanyFeatureFactory(company=company) for _ in range(20)]
        
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('onboarding_business:setup_status')
        
        # Mesurer temps
        start_time = time.time()
        response = client.get(url)
        end_time = time.time()
        
        # Vérifications
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.5, "Endpoint trop lent (>500ms)")
        
        # Vérifier données correctes
        data = response.data['data']
        self.assertEqual(len(data['brands']), 10)