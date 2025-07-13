# backend/onboarding_business/tests/test_minimal.py
from django.test import TestCase
from django.conf import settings

class MinimalTest(TestCase):
    def test_django_configured(self):
        """Test que Django est bien configuré"""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertIn('onboarding_business', settings.INSTALLED_APPS)
