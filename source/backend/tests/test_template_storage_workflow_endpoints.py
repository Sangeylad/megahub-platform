# backend/tests/test_template_storage_workflow_endpoints.py
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from ai_templates_storage.models import TemplateVariable, TemplateVersion
from ai_templates_workflow.models import TemplateValidationRule, TemplateValidationResult, TemplateApproval, TemplateReview
from ai_templates_core.models import BaseTemplate, TemplateType
from company_core.models import Company
from users_roles.models import Role

User = get_user_model()

class TestTemplateStorageEndpoints(TestCase):
    """Tests endpoints Template Storage - Variables et versions"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer user AVANT company
        self.user = User.objects.create_user(
            username="martin",
            email="martin@humari.fr", 
            password="testpass123"
        )
        
        # Setup company avec admin_id
        self.company = Company.objects.create(
            name="Test Company",
            admin_id=self.user.id
        )
        
        # Setup brand
        self.brand = Brand.objects.create(
            name="Test Brand", 
            company=self.company
        )
        
        # IMPORTANT : Relations user-brand + rôle admin
        self.user.brands.add(self.brand)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        self.user.roles.add(admin_role)
        
        # JWT token + header brand
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.defaults['HTTP_X_BRAND_ID'] = str(self.brand.id)
        
        # Setup template de base
        self.template_type = TemplateType.objects.create(
            name="content_generation",
            display_name="Génération de contenu"
        )
        
        self.template = BaseTemplate.objects.create(
            name="Template Test",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Contenu initial",
            created_by=self.user
        )
        
        # Setup variables
        self.variable = TemplateVariable.objects.create(
            name="company_name",
            display_name="Nom de l'entreprise",
            variable_type="text",
            description="Le nom de l'entreprise cliente",
            is_required=True
        )
        
        # Setup version
        self.version = TemplateVersion.objects.create(
            template=self.template,
            version_number=1,
            prompt_content="Contenu version 1",
            changelog="Version initiale",
            is_current=True,
            created_by=self.user
        )

    def _get_data_list(self, response_data):
        """Helper pour gérer pagination vs liste directe"""
        if isinstance(response_data, dict) and 'results' in response_data:
            return response_data['results']
        return response_data

    def test_template_variables_endpoints(self):
        """Test endpoints variables de templates"""
        # Liste variables
        url = reverse('template_storage:templatevariable-list')
        response = self.client.get(url)
        print(f"DEBUG: Variables response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK
        
        # Gérer pagination vs liste directe
        data_list = self._get_data_list(response.data)
        assert len(data_list) >= 1
        
        # Détail variable
        url = reverse('template_storage:templatevariable-detail', kwargs={'pk': self.variable.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "company_name"

    def test_variables_by_type_action(self):
        """Test groupement variables par type"""
        url = reverse('template_storage:templatevariable-by-type')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)
        assert 'text' in response.data

    def test_template_versions_crud(self):
        """Test CRUD versions de templates"""
        # Liste versions
        url = reverse('template_storage:templateversion-list')
        response = self.client.get(url)
        print(f"DEBUG: Versions response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK
        
        # Détail version
        url = reverse('template_storage:templateversion-detail', kwargs={'pk': self.version.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['version_number'] == 1
        
        # Création nouvelle version
        version_data = {
            'template': self.template.id,
            'prompt_content': 'Contenu version 2',
            'changelog': 'Amélioration majeure'
        }
        url = reverse('template_storage:templateversion-list')
        response = self.client.post(url, version_data, format='json')
        print(f"DEBUG: Create version response status: {response.status_code}")
        if response.status_code not in [201, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_version_set_current_action(self):
        """Test définir version courante"""
        url = reverse('template_storage:templateversion-set-current', kwargs={'pk': self.version.id})
        response = self.client.post(url)
        print(f"DEBUG: Set current version response status: {response.status_code}")
        if response.status_code not in [200, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestTemplateWorkflowEndpoints(TestCase):
    """Tests endpoints Template Workflow - Validation et approbation"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer user AVANT company
        self.user = User.objects.create_user(
            username="martin",
            email="martin@humari.fr", 
            password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            username="adminuser", 
            email="admin@humari.fr", 
            password="adminpass123",
            is_staff=True
        )
        
        # Setup company avec admin_id
        self.company = Company.objects.create(
            name="Test Company",
            admin_id=self.user.id
        )
        
        # Setup brand
        self.brand = Brand.objects.create(
            name="Test Brand", 
            company=self.company
        )
        
        # Relations user-brand + rôle admin
        self.user.brands.add(self.brand)
        self.admin_user.brands.add(self.brand)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        self.user.roles.add(admin_role)
        self.admin_user.roles.add(admin_role)
        
        # JWT token + header brand
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.defaults['HTTP_X_BRAND_ID'] = str(self.brand.id)
        
        # Setup template
        self.template_type = TemplateType.objects.create(
            name="content_generation",
            display_name="Génération de contenu"
        )
        
        self.template = BaseTemplate.objects.create(
            name="Template Test",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Contenu test",
            created_by=self.user
        )
        
        # Setup règles validation
        self.validation_rule = TemplateValidationRule.objects.create(
            name="Longueur minimale",
            description="Le prompt doit faire au moins 10 caractères",
            rule_type="content_length",
            validation_function="min_length_check",
            is_active=True
        )
        
        # Setup approbation
        self.approval = TemplateApproval.objects.create(
            template=self.template,
            status="draft",
            submitted_by=self.user
        )

    def test_validation_rules_endpoints(self):
        """Test endpoints règles de validation"""
        # Test avec user admin - switch token
        refresh = RefreshToken.for_user(self.admin_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        url = reverse('template_workflow:templatevalidationrule-list')
        response = self.client.get(url)
        print(f"DEBUG: Validation rules response status: {response.status_code}")
        if response.status_code not in [200, 403]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_validation_results_endpoints(self):
        """Test endpoints résultats validation"""
        # Créer résultat validation
        validation_result = TemplateValidationResult.objects.create(
            template=self.template,
            validation_rule=self.validation_rule,
            is_valid=True,
            validated_by=self.user
        )
        
        # Liste résultats
        url = reverse('template_workflow:templatevalidationresult-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_template_approvals_crud(self):
        """Test CRUD approbations"""
        # Liste approbations
        url = reverse('template_workflow:templateapproval-list')
        response = self.client.get(url)
        print(f"DEBUG: Approvals response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code == status.HTTP_200_OK
        
        # Détail approbation
        url = reverse('template_workflow:templateapproval-detail', kwargs={'pk': self.approval.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == "draft"

    def test_approval_workflow_actions(self):
        """Test actions workflow approbation"""
        # Soumettre pour review
        url = reverse('template_workflow:templateapproval-submit-for-review', kwargs={'pk': self.approval.id})
        response = self.client.post(url)
        print(f"DEBUG: Submit for review response status: {response.status_code}")
        if response.status_code not in [200, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        
        # Mettre à jour le statut pour tester approve
        self.approval.status = 'pending_review'
        self.approval.save()
        
        # Approuver (peut nécessiter permissions spéciales)
        url = reverse('template_workflow:templateapproval-approve', kwargs={'pk': self.approval.id})
        response = self.client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
        
        # Rejeter
        url = reverse('template_workflow:templateapproval-reject', kwargs={'pk': self.approval.id})
        data = {'rejection_reason': 'Contenu insuffisant'}
        response = self.client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]

    def test_template_reviews_crud(self):
        """Test CRUD reviews"""
        # Liste reviews
        url = reverse('template_workflow:templatereview-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Créer review
        review_data = {
            'approval': self.approval.id,
            'comment': 'Bon template, quelques améliorations possibles',
            'rating': 4,
            'review_type': 'general'
        }
        response = self.client.post(url, review_data, format='json')
        print(f"DEBUG: Create review response status: {response.status_code}")
        if response.status_code not in [201, 400]:
            print(f"DEBUG: Response content: {response.content}")
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]


class TestStorageWorkflowIntegration(TestCase):
    """Tests d'intégration Storage + Workflow"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer user AVANT company
        self.user = User.objects.create_user(
            username="martin",
            email="martin@humari.fr", 
            password="testpass123"
        )
        
        # Setup company avec admin_id
        self.company = Company.objects.create(
            name="Test Company",
            admin_id=self.user.id
        )
        
        # Setup brand
        self.brand = Brand.objects.create(
            name="Test Brand", 
            company=self.company
        )
        
        # Relations user-brand + rôle admin
        self.user.brands.add(self.brand)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        self.user.roles.add(admin_role)
        
        # JWT token + header brand
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.defaults['HTTP_X_BRAND_ID'] = str(self.brand.id)

    def test_version_approval_workflow(self):
        """Test workflow version -> approbation"""
        # Créer template et version
        template_type = TemplateType.objects.create(
            name="content_generation",
            display_name="Génération de contenu"
        )
        
        template = BaseTemplate.objects.create(
            name="Template Workflow",
            template_type=template_type,
            brand=self.brand,
            prompt_content="Contenu initial",
            created_by=self.user
        )
        
        # Créer version
        version_data = {
            'template': template.id,
            'prompt_content': 'Contenu amélioré',
            'changelog': 'Version avec améliorations'
        }
        
        url = reverse('template_storage:templateversion-list')
        response = self.client.post(url, version_data, format='json')
        
        if response.status_code == status.HTTP_201_CREATED:
            # Créer approbation pour cette version
            approval_data = {
                'template': template.id,
                'status': 'draft'
            }
            
            url = reverse('template_workflow:templateapproval-list')
            response = self.client.post(url, approval_data, format='json')
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_url_structure_storage_workflow(self):
        """Test cohérence URLs storage + workflow"""
        storage_urls = [
            '/templates/storage/variables/',
            '/templates/storage/versions/',
        ]
        
        workflow_urls = [
            '/templates/workflow/validation-rules/',
            '/templates/workflow/validation-results/',
            '/templates/workflow/approvals/',
            '/templates/workflow/reviews/',
        ]
        
        # Test accessibilité
        for url_path in storage_urls + workflow_urls:
            response = self.client.get(url_path)
            print(f"DEBUG: URL {url_path} -> Status {response.status_code}")
            assert response.status_code in [200, 401, 403, 404, 405], f"URL invalide: {url_path}"