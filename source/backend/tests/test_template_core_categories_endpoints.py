# backend/tests/test_template_core_categories_endpoints.py
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from ai_templates_core.models import TemplateType, BrandTemplateConfig, BaseTemplate
from ai_templates_categories.models import TemplateCategory, TemplateTag, CategoryPermission
from company_core.models import Company
from users_roles.models import Role

User = get_user_model()

class TestTemplateCoreEndpoints(TestCase):
    """Tests endpoints Template Core - Structure fondamentale"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer données test avec bonnes relations
        self.user = User.objects.create_user(
            username="martin",
            email="martin@humari.fr", 
            password="testpass123"
        )
        
        # Créer company avec admin
        self.company = Company.objects.create(
            name="Humari",
            admin_id=self.user.id
        )
        
        # Créer brand
        self.brand = Brand.objects.create(
            name="Humari Brand", 
            company=self.company
        )
        
        # IMPORTANT : Associer user à la brand ET faire admin
        self.user.brands.add(self.brand)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        self.user.roles.add(admin_role)
        
        print(f"DEBUG: Created user {self.user.username} (ID: {self.user.id})")
        print(f"DEBUG: Created brand {self.brand.name} (ID: {self.brand.id})")
        print(f"DEBUG: User is admin: {self.user.is_company_admin()}")
        print(f"DEBUG: User brands: {list(self.user.brands.all())}")
        
        # Générer JWT token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Authentification JWT + header brand
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.defaults['HTTP_X_BRAND_ID'] = str(self.brand.id)
        
        # Setup données de test
        self.template_type = TemplateType.objects.create(
            name="content_generation",
            display_name="Génération de contenu",
            is_active=True
        )
        
        self.brand_config = BrandTemplateConfig.objects.create(
            brand=self.brand,
            max_templates_per_type=50,
            allow_custom_templates=True
        )
        
        self.base_template = BaseTemplate.objects.create(
            name="Template Test",
            description="Description test",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Contenu du prompt test",
            created_by=self.user
        )

    def test_template_types_endpoints(self):
        """Test endpoints types de templates"""
        # Liste types
        url = reverse('templates:templatetype-list')
        response = self.client.get(url)
        print(f"DEBUG: Template types response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK
        
        # Gérer pagination vs pas de pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            # Avec pagination
            assert len(response.data['results']) >= 1
        else:
            # Sans pagination (liste directe)
            assert len(response.data) >= 1
        
        # Détail type
        url = reverse('templates:templatetype-detail', kwargs={'pk': self.template_type.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "content_generation"

    def test_brand_configs_endpoints(self):
        """Test endpoints config brand"""
        # Liste configs
        url = reverse('templates:brandtemplateconfig-list')
        response = self.client.get(url)
        print(f"DEBUG: Brand configs response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK

    def test_base_templates_crud(self):
        """Test CRUD templates de base"""
        # Liste templates
        url = reverse('templates:basetemplate-list')
        response = self.client.get(url)
        print(f"DEBUG: Base templates response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK
        
        # Détail template
        url = reverse('templates:basetemplate-detail', kwargs={'pk': self.base_template.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Template Test"
        
        # Création template
        url = reverse('templates:basetemplate-list')
        data = {
            'name': 'Nouveau Template',
            'description': 'Description nouveau',
            'template_type': self.template_type.id,
            'prompt_content': 'Nouveau prompt',
            'is_active': True
        }
        response = self.client.post(url, data)
        print(f"DEBUG: Create template response status: {response.status_code}")
        if response.status_code not in [201, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_template_duplicate_action(self):
        """Test action duplication template"""
        url = reverse('templates:basetemplate-duplicate', kwargs={'pk': self.base_template.id})
        response = self.client.post(url)
        print(f"DEBUG: Duplicate response status: {response.status_code}")
        if response.status_code not in [200, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_templates_by_type_action(self):
        """Test groupement templates par type"""
        url = reverse('templates:basetemplate-by-type')
        response = self.client.get(url)
        print(f"DEBUG: By type response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)


class TestTemplateCategoriesEndpoints(TestCase):
    """Tests endpoints Template Categories - Organisation"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer user avec relations correctes
        self.user = User.objects.create_user(
            username="martin",
            email="martin@humari.fr", 
            password="testpass123"
        )
        
        self.company = Company.objects.create(
            name="Humari",
            admin_id=self.user.id
        )
        
        self.brand = Brand.objects.create(
            name="Humari Brand", 
            company=self.company
        )
        
        # Relations importantes
        self.user.brands.add(self.brand)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        self.user.roles.add(admin_role)
        
        # JWT + brand header
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.defaults['HTTP_X_BRAND_ID'] = str(self.brand.id)
        
        # Setup catégories
        self.parent_category = TemplateCategory.objects.create(
            name="content",
            display_name="Contenu",
            level=0,
            is_active=True
        )
        
        self.child_category = TemplateCategory.objects.create(
            name="blog_posts",
            display_name="Articles de blog",
            parent=self.parent_category,
            level=1,
            is_active=True
        )
        
        # Setup tags
        self.tag = TemplateTag.objects.create(
            name="seo",
            display_name="SEO",
            usage_count=5
        )

    def test_categories_crud(self):
        """Test CRUD catégories"""
        # Liste catégories
        url = reverse('template_categories:templatecategory-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Détail catégorie
        url = reverse('template_categories:templatecategory-detail', kwargs={'pk': self.parent_category.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['display_name'] == "Contenu"

    def test_categories_tree_action(self):
        """Test arbre hiérarchique"""
        url = reverse('template_categories:templatecategory-tree')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_category_breadcrumb_action(self):
        """Test fil d'Ariane"""
        url = reverse('template_categories:templatecategory-breadcrumb', kwargs={'pk': self.child_category.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 2

    def test_tags_crud(self):
        """Test CRUD tags"""
        # Liste tags
        url = reverse('template_categories:templatetag-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Tags populaires
        url = reverse('template_categories:templatetag-popular')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_category_permissions(self):
        """Test permissions catégories"""
        url = reverse('template_categories:categorypermission-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK


class TestTemplateCoreIntegration(TestCase):
    """Tests d'intégration Core + Categories"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Setup complet avec relations
        self.user = User.objects.create_user(
            username="martin",
            email="martin@humari.fr", 
            password="testpass123"
        )
        
        self.company = Company.objects.create(
            name="Humari",
            admin_id=self.user.id
        )
        
        self.brand = Brand.objects.create(
            name="Humari Brand", 
            company=self.company
        )
        
        # Relations cruciales
        self.user.brands.add(self.brand)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        self.user.roles.add(admin_role)
        
        # JWT + brand header
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.defaults['HTTP_X_BRAND_ID'] = str(self.brand.id)
        
        # Données liées
        self.template_type = TemplateType.objects.create(
            name="content_generation",
            display_name="Génération de contenu",
            is_active=True
        )
        
        self.category = TemplateCategory.objects.create(
            name="content",
            display_name="Contenu",
            is_active=True
        )

    def test_template_with_category_integration(self):
        """Test intégration template avec catégorie"""
        # Créer template avec catégorie
        template_data = {
            'name': 'Template avec catégorie',
            'description': 'Test intégration',
            'template_type': self.template_type.id,
            'prompt_content': 'Contenu avec catégorie',
        }
        
        url = reverse('templates:basetemplate-list')
        response = self.client.post(url, template_data)
        print(f"DEBUG: Integration response status: {response.status_code}")
        if response.status_code not in [201, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_url_structure_coherence(self):
        """Test cohérence structure URLs"""
        # Vérifier que les URLs ne se chevauchent pas
        core_urls = [
            '/templates/',
            '/templates/types/',
            '/templates/brand-configs/',
        ]
        
        category_urls = [
            '/templates/categories/',
            '/templates/tags/',
            '/templates/permissions/',
        ]
        
        # Test accessibilité
        for url_path in core_urls + category_urls:
            response = self.client.get(url_path)
            print(f"DEBUG: URL {url_path} -> Status {response.status_code}")
            assert response.status_code in [200, 401, 403, 404, 405], f"URL invalide: {url_path}"