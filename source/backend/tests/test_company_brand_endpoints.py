# backend/tests/test_company_brand_endpoints.py
import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

# Models
from company_core.models.company import Company
from users_core.models.user import CustomUser
from brands_core.models.brand import Brand
from company_slots.models.slots import CompanySlots

# ✅ AJOUT : Import du helper JWT
from tests.utils.test_helpers import JWTTestMixin

User = get_user_model()

class CompanyEndpointsTestCase(JWTTestMixin, APITestCase):
    """Tests des endpoints Companies avec JWT Auth"""
    
    def setUp(self):
        """Setup pour tous les tests companies"""
        # Créer company admin
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        # Créer company
        self.company = Company.objects.create(
            name="Test Company",
            admin=self.admin_user,
            billing_email="billing@test.com"
        )
        
        # Lier admin à company
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer slots
        self.slots = CompanySlots.objects.create(
            company=self.company,
            brands_slots=5,
            users_slots=10,
            current_brands_count=0,
            current_users_count=1  # Admin déjà compté
        )
        
        # Créer brand member
        self.brand_user = CustomUser.objects.create_user(
            username='brand_member',
            email='member@test.com',
            password='testpass123',
            company=self.company,
            user_type='brand_member'
        )
        
        # Créer brand
        self.brand = Brand.objects.create(
            company=self.company,
            name="Test Brand",
            brand_admin=self.brand_user
        )
        
        # ✅ MODIFICATION : Setup JWT au lieu de force_authenticate
        self.auth_headers = self.setup_jwt_auth(self.admin_user, self.brand)
        
        # API Client
        self.client = APIClient()
    
    def test_companies_list_endpoint(self):
        """✅ Test GET /companies/ - Liste des entreprises"""
        # Test sans auth
        response = self.client.get('/companies/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # ✅ MODIFICATION : Utiliser JWT headers
        response = self.client.get('/companies/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1  # Seulement sa company
        assert data['results'][0]['name'] == 'Test Company'
        
        print("✅ Companies list endpoint")
    
    def test_companies_create_endpoint_superuser_only(self):
        """✅ Test POST /companies/ - Création d'entreprise (superuser seulement)"""
        # Test avec admin normal (doit échouer)
        company_data = {
            'name': 'Forbidden Company',
            'billing_email': 'forbidden@company.com'
        }
        
        response = self.client.post('/companies/', company_data, **self.auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Test avec superuser
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # ✅ Renouveler le token avec superuser
        self.auth_headers = self.setup_jwt_auth(self.admin_user, self.brand)
        
        response = self.client.post('/companies/', company_data, **self.auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        print("✅ Companies create endpoint superuser only")
    
    def test_companies_detail_endpoint(self):
        """✅ Test GET /companies/{id}/ - Détail d'une entreprise"""
        response = self.client.get(f'/companies/{self.company.id}/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['name'] == 'Test Company'
        assert data['admin']['username'] == 'admin_test'
        
        print("✅ Companies detail endpoint")
    
    def test_companies_update_endpoint(self):
        """✅ Test PUT/PATCH /companies/{id}/ - Mise à jour d'une entreprise"""
        update_data = {
            'name': 'Updated Company Name',
            'billing_email': 'updated@company.com'
        }
        
        response = self.client.patch(f'/companies/{self.company.id}/', update_data, **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier la mise à jour
        self.company.refresh_from_db()
        assert self.company.name == 'Updated Company Name'
        
        print("✅ Companies update endpoint")
    
    def test_companies_check_limits_action(self):
        """✅ Test POST /companies/{id}/check_limits/"""
        response = self.client.post(f'/companies/{self.company.id}/check_limits/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'alerts' in data
        assert data['company'] == 'Test Company'
        
        print("✅ Companies check limits action")
    
    def test_companies_usage_stats_action(self):
        """✅ Test GET /companies/{id}/usage_stats/"""
        response = self.client.get(f'/companies/{self.company.id}/usage_stats/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'slots' in data
        assert 'activity' in data
        
        print("✅ Companies usage stats action")
    
    def test_companies_upgrade_slots_action(self):
        """✅ Test POST /companies/{id}/upgrade_slots/"""
        upgrade_data = {
            'brands_slots': 10,
            'users_slots': 20
        }
        
        response = self.client.post(f'/companies/{self.company.id}/upgrade_slots/', upgrade_data, **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'message' in data
        assert data['brands_slots'] == 10
        assert data['users_slots'] == 20
        
        print("✅ Companies upgrade slots action")
    
    def test_companies_permissions_isolation(self):
        """✅ Test isolation des permissions entre companies"""
        # Créer une autre company
        other_admin = CustomUser.objects.create_user(
            username='other_admin',
            email='other@test.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        other_company = Company.objects.create(
            name="Other Company",
            admin=other_admin,
            billing_email="billing@other.com"
        )
        
        other_admin.company = other_company
        other_admin.save()
        
        # Admin ne doit voir que sa company
        response = self.client.get('/companies/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Test Company'  # Pas "Other Company"
        
        print("✅ Companies permissions isolation")


class BrandEndpointsTestCase(JWTTestMixin, APITestCase):
    """Tests des endpoints Brands avec JWT Auth"""
    
    def setUp(self):
        """Setup pour tous les tests brands"""
        # Setup de base (même que companies)
        self.admin_user = CustomUser.objects.create_user(
            username='brand_admin',
            email='brand@test.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="Brand Test Company",
            admin=self.admin_user,
            billing_email="billing@brand.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer brand user
        self.brand_user = CustomUser.objects.create_user(
            username='brand_user',
            email='branduser@test.com',
            password='testpass123',
            company=self.company,
            user_type='brand_member'
        )
        
        # Créer brand
        self.brand = Brand.objects.create(
            company=self.company,
            name="Test Brand",
            brand_admin=self.brand_user
        )
        
        # ✅ Setup JWT
        self.auth_headers = self.setup_jwt_auth(self.admin_user, self.brand)
        
        self.client = APIClient()
    
    def test_brands_list_endpoint(self):
        """✅ Test GET /brands/ - Liste des marques"""
        response = self.client.get('/brands/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Test Brand'
        
        print("✅ Brands list endpoint")
    
    def test_brands_create_endpoint(self):
        """✅ Test POST /brands/ - Création de marque"""
        brand_data = {
            'company': self.company.id,
            'name': 'New Brand',
            'description': 'New brand for testing',
            'url': 'https://newbrand.com',
            'brand_admin': self.brand_user.id
        }
        
        response = self.client.post('/brands/', brand_data, **self.auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data['name'] == 'New Brand'
        assert data['company'] == self.company.id
        
        print("✅ Brands create endpoint")
    
    def test_brands_create_validation_errors(self):
        """✅ Test POST /brands/ - Erreurs de validation"""
        # Test nom déjà utilisé dans la même company
        brand_data = {
            'company': self.company.id,
            'name': 'Test Brand',  # Nom déjà utilisé
            'description': 'Duplicate brand'
        }
        
        response = self.client.post('/brands/', brand_data, **self.auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert 'name' in str(data).lower() or 'déjà' in str(data).lower()
        
        print("✅ Brands create validation errors")
    
    def test_brands_detail_endpoint(self):
        """✅ Test GET /brands/{id}/ - Détail d'une marque"""
        response = self.client.get(f'/brands/{self.brand.id}/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['name'] == 'Test Brand'
        assert data['company'] == self.company.id
        
        print("✅ Brands detail endpoint")
    
    def test_brands_update_endpoint(self):
        """✅ Test PUT/PATCH /brands/{id}/ - Mise à jour d'une marque"""
        update_data = {
            'name': 'Updated Brand Name',
            'description': 'Updated description'
        }
        
        response = self.client.patch(f'/brands/{self.brand.id}/', update_data, **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier la mise à jour
        self.brand.refresh_from_db()
        assert self.brand.name == 'Updated Brand Name'
        
        print("✅ Brands update endpoint")
    
    def test_brands_assign_users_action(self):
        """✅ Test POST /brands/{id}/assign_users/"""
        assign_data = {
            'user_ids': [self.brand_user.id]
        }
        
        response = self.client.post(f'/brands/{self.brand.id}/assign_users/', assign_data, **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['assigned_users'] == 1
        
        print("✅ Brands assign users action")
    
    def test_brands_remove_users_action(self):
        """✅ Test POST /brands/{id}/remove_users/"""
        # ✅ CORRECTION : S'assurer que l'assignation est persistée
        self.brand.users.add(self.brand_user)
        self.brand.refresh_from_db()  # Forcer le reload
        
        # Vérifier que l'utilisateur est bien assigné
        assert self.brand.users.filter(id=self.brand_user.id).exists()
        
        remove_data = {
            'user_ids': [self.brand_user.id]
        }
        
        response = self.client.post(f'/brands/{self.brand.id}/remove_users/', remove_data, **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['removed_users'] == 1
        
        print("✅ Brands remove users action")
    
    def test_brands_accessible_users_action(self):
        """✅ Test GET /brands/{id}/accessible_users/"""
        response = self.client.get(f'/brands/{self.brand.id}/accessible_users/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'users' in data
        assert data['brand'] == 'Test Brand'
        
        print("✅ Brands accessible users action")
    
    def test_brands_set_admin_action(self):
        """✅ Test POST /brands/{id}/set_admin/"""
        admin_data = {
            'user_id': self.admin_user.id
        }
        
        response = self.client.post(f'/brands/{self.brand.id}/set_admin/', admin_data, **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'message' in data
        assert data['new_admin'] == 'brand_admin'
        
        print("✅ Brands set admin action")
    
    def test_brands_toggle_active_action(self):
        """✅ Test POST /brands/{id}/toggle_active/"""
        response = self.client.post(f'/brands/{self.brand.id}/toggle_active/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'is_active' in data
        
        print("✅ Brands toggle active action")
    
    def test_brands_by_company_action(self):
        """✅ Test GET /brands/by_company/"""
        response = self.client.get('/brands/by_company/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'brands_by_company' in data
        assert 'Brand Test Company' in data['brands_by_company']
        
        print("✅ Brands by company action")


class BrandAdvancedEndpointsTestCase(JWTTestMixin, APITestCase):
    """Tests avancés des endpoints Brands avec JWT Auth"""
    
    def setUp(self):
        """Setup pour tests avancés"""
        self.admin_user = CustomUser.objects.create_user(
            username='advanced_admin',
            email='advanced@test.com',
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
        
        # Créer slots avec limite basse
        self.slots = CompanySlots.objects.create(
            company=self.company,
            brands_slots=2,  # Limite basse pour tester
            users_slots=10,
            current_brands_count=0,
            current_users_count=1
        )
        
        # Créer brand de base
        self.brand = Brand.objects.create(
            company=self.company,
            name="Base Brand"
        )
        
        # ✅ Setup JWT
        self.auth_headers = self.setup_jwt_auth(self.admin_user, self.brand)
        
        self.client = APIClient()
    
    def test_brands_assign_users_different_company_error(self):
        """✅ Test POST /brands/{id}/assign_users/ - Erreur utilisateur autre company"""
        # Créer utilisateur d'une autre company
        other_user = CustomUser.objects.create_user(
            username='other_user',
            email='other@company.com',
            password='testpass123'
        )
        
        assign_data = {
            'user_ids': [other_user.id]
        }
        
        response = self.client.post(f'/brands/{self.brand.id}/assign_users/', assign_data, **self.auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        print("✅ Brands assign users different company error")
    
    def test_brands_create_slots_limit_reached(self):
        """✅ Test POST /brands/ - Limite de slots atteinte"""
        # Créer 2 brands pour atteindre la limite
        Brand.objects.create(company=self.company, name="Brand 1")
        Brand.objects.create(company=self.company, name="Brand 2")
        
        # Mettre à jour le compteur
        self.slots.update_brands_count()
        
        # Essayer de créer une autre brand (doit échouer)
        brand_data = {
            'company': self.company.id,
            'name': 'Over Limit Brand'
        }
        
        response = self.client.post('/brands/', brand_data, **self.auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Vérifier que l'erreur concerne la limite
        data = response.json()
        assert 'limite' in str(data).lower() or 'slots' in str(data).lower()
        
        print("✅ Brands create slots limit reached")
    
    def test_brands_soft_delete_integration(self):
        """✅ Test intégration SoftDeleteViewSetMixin"""
        # Créer brand
        brand = Brand.objects.create(company=self.company, name="To Delete")
        
        # Supprimer (soft delete)
        response = self.client.delete(f'/brands/{brand.id}/', **self.auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Vérifier que c'est un soft delete
        brand.refresh_from_db()
        assert brand.is_deleted == True
        
        # Vérifier qu'elle n'apparaît plus dans la liste
        response = self.client.get('/brands/', **self.auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        brand_names = [b['name'] for b in data['results']]
        assert "To Delete" not in brand_names  # Soft deleted, donc pas dans la liste
        
        print("✅ Brands soft delete integration")

print("🔧 Tests Company/Brand corrigés avec JWT Auth !")
print("📋 Commandes pour exécuter :")
print("   pytest tests/test_company_brand_endpoints.py -v")
print("   pytest tests/test_company_brand_endpoints.py::CompanyEndpointsTestCase::test_companies_list_endpoint -v")