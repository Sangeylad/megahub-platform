# backend/tests/conftest.py
import os
import django
import pytest
from django.conf import settings

def pytest_configure():
    """Configuration Django pour pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
    django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    """Setup de la DB pour les tests"""
    # PyTest Django gère automatiquement la DB de test
    pass

@pytest.fixture
def admin_user(db):
    """Fixture pour un admin user"""
    from users_core.models.user import CustomUser
    return CustomUser.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='testpass123',
        user_type='agency_admin'
    )

@pytest.fixture  
def test_company(db, admin_user):
    """Fixture pour une company de test"""
    from company_core.models.company import Company
    company = Company.objects.create(
        name="Test Company",
        admin=admin_user,
        billing_email="billing@test.com"
    )
    admin_user.company = company
    admin_user.save()
    return company
