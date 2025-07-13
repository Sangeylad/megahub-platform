# backend/onboarding_business/tests/test_onboarding.py

from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class OnboardingWorkflowIntegrationTest(APITestCase):
    """Tests d'intégration workflow onboarding complet"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_complete_onboarding_workflow(self):
        """Test workflow onboarding complet"""
        # 1. GIVEN - User sans business
        self.assertIsNone(getattr(self.user, 'company', None))
        
        # 2. WHEN - Authentification
        self.client.force_authenticate(user=self.user)
        
        # 3. THEN - Vérifier éligibilité
        response = self.client.get('/onboarding/business/check-eligibility/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['data']['is_eligible'])
        
        # 4. WHEN - Setup business (mockés pour tests unitaires)
        with patch('onboarding_business.services.onboarding.OnboardingService.setup_business_for_user') as mock_setup:
            mock_company = type('MockCompany', (), {
                'id': 1, 'name': 'Test Business',
                'is_in_trial': lambda: True,
                'trial_days_remaining': lambda: 14,
                'get_business_mode': lambda: 'solo'
            })()
            
            mock_brand = type('MockBrand', (), {
                'id': 1, 'name': 'Test Brand'
            })()
            
            mock_setup.return_value = {
                'company': mock_company,
                'brand': mock_brand,
                'slots_summary': {},
                'features_summary': {}
            }
            
            response = self.client.post('/onboarding/business/setup/', {
                'business_name': 'Test Business'
            })
            
            # 5. THEN - Business créé avec succès
            self.assertEqual(response.status_code, 201)
            self.assertTrue(response.data['success'])
            self.assertEqual(response.data['data']['company_name'], 'Test Business')


class OnboardingSystemStructureTest(TestCase):
    """Tests structure et intégrité du système onboarding"""
    
    def test_onboarding_apps_in_installed_apps(self):
        """Vérifier que toutes les apps onboarding sont installées"""
        from django.conf import settings
        
        required_apps = [
            'onboarding_registration',
            'onboarding_business',
            'onboarding_invitations',
            'onboarding_trials'
        ]
        
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS, f"App {app} manquante dans INSTALLED_APPS")
    
    def test_onboarding_services_importable(self):
        """Vérifier que tous les services sont importables"""
        try:
            from ..services.onboarding import OnboardingService
            from ..services.business_creation import create_solo_business_for_user
            from ..services.features_setup import setup_default_features
            from ..services.slots_setup import setup_default_slots
            from ..services.trial_setup import setup_trial_subscription
            from ..services.roles_setup import assign_default_roles
            
            # Si on arrive ici, tous les imports sont OK
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import service failed: {e}")
    
    def test_onboarding_exceptions_defined(self):
        """Vérifier que toutes les exceptions sont définies"""
        from ..exceptions import (
            OnboardingError, UserNotEligibleError, BusinessAlreadyExistsError,
            SlotsLimitReachedError, TrialExpiredError
        )
        
        # Vérifier héritage correct
        self.assertTrue(issubclass(UserNotEligibleError, OnboardingError))
        self.assertTrue(issubclass(BusinessAlreadyExistsError, OnboardingError))