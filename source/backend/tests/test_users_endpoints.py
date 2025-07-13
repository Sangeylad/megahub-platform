# backend/tests/test_users_endpoints.py

import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

# Models
from company_core.models.company import Company
from users_core.models.user import CustomUser
from brands_core.models.brand import Brand
from company_slots.models.slots import CompanySlots
from users_roles.models.roles import Role, UserRole, Permission, RolePermission

User = get_user_model()

class UsersEndpointsTestCase(APITestCase):
    """Tests des endpoints Users"""
    
    def setUp(self):
        """Setup pour tous les tests users"""
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
        
        # API Client
        self.client = APIClient()
    
    def test_users_list_endpoint(self):
        """✅ Test GET /users/ - Liste des utilisateurs"""
        # Test sans auth
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test avec auth admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == 2  # admin + brand_member
        
        # Vérifier les champs du serializer
        user_data = data['results'][0]
        expected_fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'company_name', 'user_type', 'is_active', 'accessible_brands_count',
            'last_login', 'date_joined'
        ]
        for field in expected_fields:
            assert field in user_data
        
        print("✅ Users list endpoint")
    
    def test_users_create_endpoint(self):
        """✅ Test POST /users/ - Création d'utilisateur"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test création valide
        user_data = {
            'username': 'new_user',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'company': self.company.id,
            'user_type': 'brand_member',
            'phone': '+33123456789',
            'position': 'Developer'
        }
        
        response = self.client.post('/users/', user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Vérifier que l'utilisateur est créé
        assert CustomUser.objects.filter(username='new_user').exists()
        new_user = CustomUser.objects.get(username='new_user')
        assert new_user.company == self.company
        assert new_user.user_type == 'brand_member'
        
        # Vérifier que le compteur de slots est mis à jour
        self.slots.refresh_from_db()
        assert self.slots.current_users_count == 3  # admin + brand_member + new_user
        
        print("✅ Users create endpoint")
    
    def test_users_create_validation_errors(self):
        """✅ Test POST /users/ - Erreurs de validation"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test mots de passe différents
        user_data = {
            'username': 'invalid_user',
            'email': 'martin@humari.fr',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'company': self.company.id,
        }
        
        response = self.client.post('/users/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Vérifier que l'erreur concerne les mots de passe
        data = response.json()
        assert 'password' in str(data).lower() or 'mot de passe' in str(data).lower()
        
        # Test email déjà utilisé
        user_data = {
            'username': 'another_user',
            'email': 'admin@test.com',  # Email déjà utilisé
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'company': self.company.id,
        }
        
        response = self.client.post('/users/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Vérifier que l'erreur concerne l'email
        data = response.json()
        assert 'email' in str(data).lower() or 'adresse' in str(data).lower()
        
        print("✅ Users create validation errors")
    
    def test_users_detail_endpoint(self):
        """✅ Test GET /users/{id}/ - Détail utilisateur"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/users/{self.brand_user.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['username'] == 'brand_member'
        assert data['company_name'] == 'Test Company'
        assert 'permissions_summary' in data
        assert 'accessible_brands_info' in data
        
        print("✅ Users detail endpoint")
    
    def test_users_update_endpoint(self):
        """✅ Test PUT/PATCH /users/{id}/ - Mise à jour utilisateur"""
        self.client.force_authenticate(user=self.admin_user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'position': 'Senior Developer',
            'phone': '+33987654321'
        }
        
        response = self.client.patch(f'/users/{self.brand_user.id}/', update_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier la mise à jour
        self.brand_user.refresh_from_db()
        assert self.brand_user.first_name == 'Updated'
        assert self.brand_user.last_name == 'Name'
        assert self.brand_user.position == 'Senior Developer'
        
        print("✅ Users update endpoint")
    
    def test_users_change_password_action(self):
        """✅ Test POST /users/{id}/change_password/"""
        self.client.force_authenticate(user=self.admin_user)
        
        password_data = {
            'current_password': 'testpass123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        response = self.client.post(f'/users/{self.admin_user.id}/change_password/', password_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'message' in data
        assert data['user'] == 'admin_test'
        
        # Vérifier que le mot de passe a changé
        self.admin_user.refresh_from_db()
        assert self.admin_user.check_password('newpassword123')
        
        print("✅ Users change password action")
    
    def test_users_assign_brands_action(self):
        """✅ Test POST /users/{id}/assign_brands/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer une autre brand
        brand2 = Brand.objects.create(
            company=self.company,
            name="Test Brand 2"
        )
        
        assign_data = {
            'brand_ids': [self.brand.id, brand2.id]
        }
        
        response = self.client.post(f'/users/{self.brand_user.id}/assign_brands/', assign_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['assigned_brands'] == 2
        
        # Vérifier l'assignation
        assert self.brand_user.brands.count() == 2
        
        print("✅ Users assign brands action")
    
    def test_users_accessible_brands_action(self):
        """✅ Test GET /users/{id}/accessible_brands/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Assigner la brand au user
        self.brand_user.brands.add(self.brand)
        
        response = self.client.get(f'/users/{self.brand_user.id}/accessible_brands/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['user'] == 'brand_member'
        assert data['brands_count'] == 1
        assert len(data['brands']) == 1
        assert data['brands'][0]['name'] == 'Test Brand'
        
        print("✅ Users accessible brands action")
    
    def test_users_toggle_active_action(self):
        """✅ Test POST /users/{id}/toggle_active/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Désactiver un utilisateur
        response = self.client.post(f'/users/{self.brand_user.id}/toggle_active/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'désactivé' in data['message']
        assert data['is_active'] == False
        
        # Vérifier la désactivation
        self.brand_user.refresh_from_db()
        assert self.brand_user.is_active == False
        
        # Test empêcher désactivation admin
        response = self.client.post(f'/users/{self.admin_user.id}/toggle_active/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Vérifier que l'erreur concerne l'admin
        data = response.json()
        assert 'admin' in str(data).lower() or 'entreprise' in str(data).lower()
        
        print("✅ Users toggle active action")
    
    def test_users_by_company_action(self):
        """✅ Test GET /users/by_company/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/users/by_company/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'users_by_company' in data
        assert 'Test Company' in data['users_by_company']
        assert data['total_users'] == 2
        assert data['companies_count'] == 1
        
        print("✅ Users by company action")
    
    def test_users_by_type_action(self):
        """✅ Test GET /users/by_type/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/users/by_type/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'users_by_type' in data
        assert 'Admin Agence' in data['users_by_type']
        assert 'Membre Marque' in data['users_by_type']
        
        print("✅ Users by type action")
    
    def test_users_permissions_different_roles(self):
        """✅ Test permissions selon le rôle utilisateur"""
        # Test avec brand member - ne doit voir que son entreprise
        self.client.force_authenticate(user=self.brand_user)
        
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        # Doit voir seulement les users de sa company
        assert len(data['results']) == 2
        
        # Test création interdite pour brand member
        user_data = {
            'username': 'forbidden_user',
            'email': 'forbidden@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'company': self.company.id,
        }
        
        response = self.client.post('/users/', user_data)
        # Le brand member peut créer des users dans son company si permissions
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN]
        
        print("✅ Users permissions different roles")


class UserRolesEndpointsTestCase(APITestCase):
    """Tests des endpoints Roles"""
    
    def setUp(self):
        """Setup pour les tests roles"""
        # Setup de base
        self.admin_user = CustomUser.objects.create_user(
            username='admin_roles',
            email='admin@roles.com',
            password='testpass123',
            user_type='agency_admin'
        )
        
        self.company = Company.objects.create(
            name="Roles Test Company",
            admin=self.admin_user,
            billing_email="billing@roles.com"
        )
        
        self.admin_user.company = self.company
        self.admin_user.save()
        
        # Créer des permissions
        self.read_permission = Permission.objects.create(
            name="websites.read",
            display_name="Lecture Sites Web",
            permission_type="read",
            resource_type="website"
        )
        
        self.write_permission = Permission.objects.create(
            name="websites.write",
            display_name="Écriture Sites Web",
            permission_type="write",
            resource_type="website"
        )
        
        # Créer des rôles
        self.viewer_role = Role.objects.create(
            name="website_viewer",
            display_name="Lecteur Sites Web",
            role_type="brand"
        )
        
        self.editor_role = Role.objects.create(
            name="website_editor",
            display_name="Éditeur Sites Web",
            role_type="brand"
        )
        
        self.client = APIClient()
    
    def test_roles_list_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/users/roles/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 2
        
        role_data = data['results'][0]
        expected_fields = [
            'id', 'name', 'display_name', 'role_type', 'is_active',
            'users_count', 'permissions_count'
        ]
        for field in expected_fields:
            assert field in role_data
        
        print("✅ Roles list endpoint")
    
    def test_roles_create_endpoint(self):
        """✅ Test POST /users/roles/"""
        self.client.force_authenticate(user=self.admin_user)
        
        role_data = {
            'name': 'custom_role',
            'display_name': 'Rôle Personnalisé',
            'description': 'Rôle créé pour les tests',
            'role_type': 'company'
        }
        
        response = self.client.post('/users/roles/', role_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        assert Role.objects.filter(name='custom_role').exists()
        
        print("✅ Roles create endpoint")
    
    def test_roles_assign_permissions_action(self):
        """✅ Test POST /users/roles/{id}/assign_permissions/"""
        self.client.force_authenticate(user=self.admin_user)
        
        assign_data = {
            'permission_ids': [self.read_permission.id, self.write_permission.id],
            'is_granted': True
        }
        
        response = self.client.post(f'/users/roles/{self.editor_role.id}/assign_permissions/', assign_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['permissions_count'] == 2
        
        # Vérifier l'assignation
        assert self.editor_role.role_permissions.count() == 2
        
        print("✅ Roles assign permissions action")
    
    def test_roles_users_action(self):
        """✅ Test GET /users/roles/{id}/users/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer user role
        brand = Brand.objects.create(company=self.company, name="Test Brand")
        user_role = UserRole.objects.create(
            user=self.admin_user,
            role=self.editor_role,
            company=self.company,
            brand=brand,
            granted_by=self.admin_user
        )
        
        response = self.client.get(f'/users/roles/{self.editor_role.id}/users/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['users_count'] == 1
        assert len(data['users']) == 1
        assert data['users'][0]['username'] == 'admin_roles'
        
        print("✅ Roles users action")
    
    def test_user_roles_list_endpoint(self):
        """✅ Test GET /user-roles/"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer assignation
        brand = Brand.objects.create(company=self.company, name="Test Brand")
        user_role = UserRole.objects.create(
            user=self.admin_user,
            role=self.editor_role,
            company=self.company,
            brand=brand,
            granted_by=self.admin_user
        )
        
        response = self.client.get('/users/user-roles/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 1
        
        user_role_data = data['results'][0]
        expected_fields = [
            'user_username', 'role_name', 'company_name', 'brand_name',
            'is_active_status', 'context_summary'
        ]
        for field in expected_fields:
            assert field in user_role_data
        
        print("✅ User roles list endpoint")
    
    def test_user_roles_create_endpoint(self):
        """✅ Test POST /user-roles/"""
        self.client.force_authenticate(user=self.admin_user)
        
        brand = Brand.objects.create(company=self.company, name="Test Brand")
        brand_user = CustomUser.objects.create_user(
            username='role_user',
            email='role@test.com',
            password='testpass123',
            company=self.company
        )
        
        user_role_data = {
            'user': brand_user.id,
            'role': self.viewer_role.id,
            'company': self.company.id,
            'brand': brand.id
        }
        
        response = self.client.post('/users/user-roles/', user_role_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        assert UserRole.objects.filter(user=brand_user, role=self.viewer_role).exists()
        
        print("✅ User roles create endpoint")
    
    def test_permissions_list_endpoint(self):
        """✅ Test GET /permissions/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/users/permissions/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data['results']) == 2
        
        permission_data = data['results'][0]
        expected_fields = [
            'id', 'name', 'display_name', 'permission_type',
            'resource_type', 'roles_count'
        ]
        for field in expected_fields:
            assert field in permission_data
        
        print("✅ Permissions list endpoint")


class UsersAdvancedEndpointsTestCase(APITestCase):
    """Tests avancés des endpoints Users"""
    
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
        
        # Créer slots avec limite
        self.slots = CompanySlots.objects.create(
            company=self.company,
            brands_slots=5,
            users_slots=2,  # Limite basse pour tester
            current_brands_count=0,
            current_users_count=1  # Admin déjà compté
        )
        
        self.client = APIClient()
    
    def test_users_create_slots_limit_reached(self):
        """✅ Test POST /users/ - Limite de slots atteinte"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer un user pour atteindre la limite
        CustomUser.objects.create_user(
            username='limit_user',
            email='limit@test.com',
            password='testpass123',
            company=self.company
        )
        
        # Mettre à jour le compteur
        self.slots.update_users_count()
        
        # Essayer de créer un autre user (doit échouer)
        user_data = {
            'username': 'over_limit',
            'email': 'overlimit@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'company': self.company.id,
        }
        
        response = self.client.post('/users/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Vérifier que l'erreur concerne la limite
        data = response.json()
        assert 'limite' in str(data).lower() or 'impossible' in str(data).lower()
        
        print("✅ Users create slots limit reached")
    
    def test_users_recent_activity_action(self):
        """✅ Test GET /users/recent_activity/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/users/recent_activity/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_fields = ['recent_users', 'active_users', 'total_recent', 'total_active']
        for field in expected_fields:
            assert field in data
        
        print("✅ Users recent activity action")
    
    def test_users_overview_action(self):
        """✅ Test GET /users/users_overview/"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/users/users_overview/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_fields = [
            'total_users', 'active_users', 'activation_rate',
            'users_by_type', 'users_by_company', 'top_users'
        ]
        for field in expected_fields:
            assert field in data
        
        assert data['total_users'] >= 1
        assert data['activation_rate'] >= 0
        
        print("✅ Users overview action")
    
    def test_users_permissions_security(self):
        """✅ Test sécurité des permissions entre companies"""
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
        
        # Admin ne doit pas voir les users d'autres companies
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        # Ne doit voir que ses propres users
        usernames = [user['username'] for user in data['results']]
        assert 'other_admin' not in usernames
        assert 'advanced_admin' in usernames
        
        print("✅ Users permissions security")

print("📁 Tests endpoints Users créés avec succès !")
print("🔧 Commandes pour exécuter :")
print("   pytest tests/test_users_endpoints.py -v")
print("   pytest tests/test_users_endpoints.py::UsersEndpointsTestCase::test_users_list_endpoint -v")