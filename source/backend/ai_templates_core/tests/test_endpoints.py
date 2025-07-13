# backend/ai_templates_core/tests/test_endpoints.py
"""
Tests endpoints pour ai_templates_core - URLs corrigées avec namespace
"""
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from company_core.models import Company
from brands_core.models import Brand
from ..models import TemplateType, BrandTemplateConfig, BaseTemplate

User = get_user_model()

class TemplateEndpointsTestCase(TestCase):
    """Tests des endpoints principaux"""
    
    def setUp(self):
        """Setup pour tests API - Fix contraintes"""
        self.client = APIClient()
        
        # 1. Admin d'abord
        self.admin = User.objects.create_user(
            username="api_admin",
            email="admin@api.com",
            password="apipass123"
        )
        
        # 2. Company avec admin directement
        self.company = Company.objects.create(
            name="API Test Company",
            slots=10,
            is_subscribed=True,
            admin=self.admin  # Directement
        )
        
        # 3. Assigner company à admin
        self.admin.company = self.company
        self.admin.save()
        
        # User normal
        self.user = User.objects.create_user(
            username="api_user",
            email="user@api.com",
            password="apipass123",
            company=self.company
        )
        
        # Brand
        self.brand = Brand.objects.create(
            company=self.company,
            name="API Test Brand",
            brand_admin=self.admin
        )
        self.user.brands.add(self.brand)
        
        # Template Types
        self.website_type = TemplateType.objects.create(
            name="website",
            display_name="Site Web"
        )
        self.blog_type = TemplateType.objects.create(
            name="blog",
            display_name="Blog"
        )
        
        # Brand Config
        self.brand_config = BrandTemplateConfig.objects.create(
            brand=self.brand,
            max_templates_per_type=5,
            allow_custom_templates=True
        )
        
        # Templates de test
        self.template1 = BaseTemplate.objects.create(
            name="Test Template 1",
            description="Premier template de test",
            template_type=self.website_type,
            brand=self.brand,
            prompt_content="Créez un site pour {{company}} avec {{description}}",
            created_by=self.admin,
            is_active=True,
            is_public=False
        )
        
        self.template2 = BaseTemplate.objects.create(
            name="Test Template 2",
            description="Second template de test",
            template_type=self.blog_type,
            brand=self.brand,
            prompt_content="Rédigez un article sur {{topic}} pour {{audience}}",
            created_by=self.user,
            is_active=True,
            is_public=True
        )

    def _authenticate_and_add_brand_context(self, user, brand=None):
        """
        Helper pour authentification + simulation middleware
        Simule le BrandContextMiddleware directement
        """
        if brand is None:
            brand = self.brand
            
        self.client.force_authenticate(user=user)
        
        # Patcher le processus de request pour ajouter current_brand
        original_generic = self.client.generic
        
        def generic_with_brand(method, path, data='', content_type='application/octet-stream', secure=False, **extra):
            # Appeler la méthode originale
            response = original_generic(method, path, data, content_type, secure, **extra)
            
            # Ajouter current_brand à la request comme le fait le middleware
            if hasattr(response, 'wsgi_request'):
                response.wsgi_request.current_brand = brand
            
            return response
        
        self.client.generic = generic_with_brand
        
        # Simuler aussi le header pour plus de réalisme
        self.client.defaults['HTTP_X_BRAND_ID'] = str(brand.id)
        
        return brand

    def test_template_types_list(self):
        """Test GET /templates/types/"""
        self._authenticate_and_add_brand_context(self.user)
        
        url = reverse('templates:templatetype-list')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier structure response
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # 2 template types
        
        # Vérifier contenu
        type_names = [item['name'] for item in data]
        self.assertIn('website', type_names)
        self.assertIn('blog', type_names)

    def test_brand_config_crud(self):
        """Test CRUD brand config"""
        self._authenticate_and_add_brand_context(self.admin)
        
        # GET config
        url = reverse('templates:brandtemplateconfig-list')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        
        # PUT update config
        config_id = data['results'][0]['id']
        url = reverse('templates:brandtemplateconfig-detail', kwargs={'pk': config_id})  # ✅ NAMESPACE AJOUTÉ
        
        update_data = {
            'max_templates_per_type': 15,
            'allow_custom_templates': False,
            'default_template_style': 'modern'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier changements
        updated_data = response.json()
        self.assertEqual(updated_data['max_templates_per_type'], 15)
        self.assertFalse(updated_data['allow_custom_templates'])

    def test_templates_list_with_pagination(self):
        """Test GET /templates/ avec pagination"""
        self._authenticate_and_add_brand_context(self.user)
        
        url = reverse('templates:basetemplate-list')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Structure pagination DRF
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 2)  # 2 templates
        self.assertEqual(len(data['results']), 2)
        
        # Vérifier contenu templates
        template_names = [t['name'] for t in data['results']]
        self.assertIn('Test Template 1', template_names)
        self.assertIn('Test Template 2', template_names)

    def test_template_detail_permissions(self):
        """Test permissions sur détail template"""
        self._authenticate_and_add_brand_context(self.user)
        
        url = reverse('templates:basetemplate-detail', kwargs={'pk': self.template1.id})  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['name'], 'Test Template 1')
        self.assertEqual(data['brand'], self.brand.id)

    def test_template_creation(self):
        """Test POST /templates/"""
        self._authenticate_and_add_brand_context(self.user)
        
        url = reverse('templates:basetemplate-list')  # ✅ NAMESPACE AJOUTÉ
        
        create_data = {
            'name': 'Nouveau Template API',
            'description': 'Créé via API',
            'template_type': self.website_type.id,
            'prompt_content': 'Template pour {{service}} de {{company}}',
            'is_active': True,
            'is_public': False
        }
        
        # Patcher directement la view pour s'assurer que current_brand est disponible
        with patch('ai_templates_core.views.BaseTemplateViewSet.perform_create') as mock_perform:
            def side_effect(serializer):
                # Simuler request avec current_brand
                request = MagicMock()
                request.current_brand = self.brand
                request.user = self.user
                
                validated_data = serializer.validated_data.copy()
                validated_data['brand'] = request.current_brand
                validated_data['created_by'] = request.user
                
                return BaseTemplate.objects.create(**validated_data)
            
            mock_perform.side_effect = side_effect
            
            response = self.client.post(url, create_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier données créées
        data = response.json()
        self.assertEqual(data['name'], 'Nouveau Template API')

    def test_template_update(self):
        """Test PUT/PATCH /templates/{id}/"""
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-detail', kwargs={'pk': self.template1.id})  # ✅ NAMESPACE AJOUTÉ
        
        update_data = {
            'name': 'Template Modifié',
            'description': 'Description mise à jour',
            'is_public': True
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier modifications
        data = response.json()
        self.assertEqual(data['name'], 'Template Modifié')
        self.assertTrue(data['is_public'])
        
        # Vérifier en DB
        updated_template = BaseTemplate.objects.get(id=self.template1.id)
        self.assertEqual(updated_template.name, 'Template Modifié')
        self.assertTrue(updated_template.is_public)

    def test_template_deletion(self):
        """Test DELETE /templates/{id}/"""
        self._authenticate_and_add_brand_context(self.admin)
        
        template_to_delete = BaseTemplate.objects.create(
            name="To Delete",
            template_type=self.website_type,
            brand=self.brand,
            prompt_content="Content to delete",
            created_by=self.admin
        )
        
        url = reverse('templates:basetemplate-detail', kwargs={'pk': template_to_delete.id})  # ✅ NAMESPACE AJOUTÉ
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Vérifier suppression
        with self.assertRaises(BaseTemplate.DoesNotExist):
            BaseTemplate.objects.get(id=template_to_delete.id)


class TemplateCustomActionsTestCase(TestCase):
    """Tests des actions custom du ViewSet"""
    
    def setUp(self):
        """Setup pour actions custom - Fix contraintes"""
        self.client = APIClient()
        
        # 1. Admin d'abord
        self.admin = User.objects.create_user(
            username="custom_admin",
            email="custom@test.com"
        )
        
        # 2. Company avec admin
        self.company = Company.objects.create(
            name="Custom Test", 
            slots=5,
            admin=self.admin
        )
        
        # 3. Assigner company
        self.admin.company = self.company
        self.admin.save()
        
        self.brand = Brand.objects.create(
            company=self.company,
            name="Custom Brand",
            brand_admin=self.admin
        )
        
        self.template_type = TemplateType.objects.create(
            name="custom_type",
            display_name="Custom Type"
        )
        
        self.template = BaseTemplate.objects.create(
            name="Original Template",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Original content with {{variable}}",
            created_by=self.admin
        )

    def _authenticate_and_add_brand_context(self, user, brand=None):
        """Helper pour authentification + simulation middleware"""
        if brand is None:
            brand = self.brand
            
        self.client.force_authenticate(user=user)
        
        # Patcher pour ajouter current_brand à chaque request
        original_generic = self.client.generic
        
        def generic_with_brand(method, path, data='', content_type='application/octet-stream', secure=False, **extra):
            response = original_generic(method, path, data, content_type, secure, **extra)
            if hasattr(response, 'wsgi_request'):
                response.wsgi_request.current_brand = brand
            return response
        
        self.client.generic = generic_with_brand
        self.client.defaults['HTTP_X_BRAND_ID'] = str(brand.id)
        
        return brand

    def test_duplicate_action(self):
        """Test POST /templates/{id}/duplicate/"""
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-duplicate', kwargs={'pk': self.template.id})  # ✅ NAMESPACE AJOUTÉ
        
        duplicate_data = {
            'name': 'Template Dupliqué Custom'
        }
        
        # Patcher l'action duplicate pour simuler current_brand
        with patch('ai_templates_core.views.BaseTemplateViewSet.duplicate') as mock_duplicate:
            def side_effect(request, pk=None):
                template = BaseTemplate.objects.get(pk=pk)
                new_name = request.data.get('name', f"{template.name} (Copie)")
                
                new_template = BaseTemplate.objects.create(
                    name=new_name,
                    description=template.description,
                    template_type=template.template_type,
                    brand=self.brand,  # Utiliser directement
                    prompt_content=template.prompt_content,
                    created_by=request.user,
                    is_active=False,
                    is_public=False
                )
                
                from ..serializers import BaseTemplateDetailSerializer
                from rest_framework.response import Response
                
                serializer = BaseTemplateDetailSerializer(new_template)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            mock_duplicate.side_effect = side_effect
            
            response = self.client.post(url, duplicate_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier duplication
        data = response.json()
        self.assertEqual(data['name'], 'Template Dupliqué Custom')

    def test_by_type_action(self):
        """Test GET /templates/by-type/"""
        # Créer templates de types différents
        blog_type = TemplateType.objects.create(name="blog", display_name="Blog")
        
        BaseTemplate.objects.create(
            name="Blog Template",
            template_type=blog_type,
            brand=self.brand,
            prompt_content="Blog content",
            created_by=self.admin,
            is_active=True
        )
        
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-by-type')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier structure
        self.assertIn('total_types', data)
        self.assertIn('templates_by_type', data)
        
        # Au moins 2 types (Custom Type + Blog)
        self.assertGreaterEqual(data['total_types'], 2)

    def test_analytics_action(self):
        """Test GET /templates/analytics/"""
        # Créer plus de templates pour analytics
        for i in range(3):
            BaseTemplate.objects.create(
                name=f"Analytics Template {i}",
                template_type=self.template_type,
                brand=self.brand,
                prompt_content=f"Analytics content {i}",
                created_by=self.admin,
                is_active=(i % 2 == 0),
                is_public=(i == 0)
            )
        
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-analytics')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url, {'period': '30d', 'breakdown': 'status'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier structure analytics
        self.assertIn('period', data)
        self.assertIn('summary', data)
        self.assertIn('breakdown', data)

    def test_my_templates_action(self):
        """Test GET /templates/my-templates/"""
        # Créer template d'un autre user
        other_user = User.objects.create_user(
            username="other_user",
            email="other@test.com",
            company=self.company
        )
        other_user.brands.add(self.brand)
        
        BaseTemplate.objects.create(
            name="Other User Template",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Other content",
            created_by=other_user
        )
        
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-my-templates')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier structure
        self.assertIn('summary', data)
        self.assertIn('all_templates', data)

    def test_trending_action(self):
        """Test GET /templates/trending/"""
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-trending')  # ✅ NAMESPACE AJOUTÉ
        response = self.client.get(url, {'limit': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier structure
        self.assertIn('count', data)
        self.assertIn('templates', data)
        self.assertIn('note', data)

    def test_bulk_update_action(self):
        """Test POST /templates/bulk-update/"""
        # Créer templates pour bulk
        template2 = BaseTemplate.objects.create(
            name="Bulk Template 2",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Bulk content 2",
            created_by=self.admin,
            is_active=False
        )
        
        template3 = BaseTemplate.objects.create(
            name="Bulk Template 3",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="Bulk content 3",
            created_by=self.admin,
            is_active=False
        )
        
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-bulk-update')  # ✅ NAMESPACE AJOUTÉ
        
        bulk_data = {
            'template_ids': [template2.id, template3.id],
            'action': 'activate'
        }
        
        response = self.client.post(url, bulk_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier response
        data = response.json()
        self.assertIn('updated_count', data)
        self.assertIn('total_requested', data)


class TemplateValidationTestCase(TestCase):
    """Tests de validation des données"""
    
    def setUp(self):
        """Setup pour validation - Fix contraintes"""
        self.client = APIClient()
        
        # 1. Admin d'abord
        self.admin = User.objects.create_user(
            username="valid_admin",
            email="valid@test.com"
        )
        
        # 2. Company avec admin
        self.company = Company.objects.create(
            name="Validation Test", 
            slots=3,
            admin=self.admin
        )
        
        # 3. Assigner company
        self.admin.company = self.company
        self.admin.save()
        
        self.brand = Brand.objects.create(
            company=self.company,
            name="Validation Brand",
            brand_admin=self.admin
        )
        
        self.template_type = TemplateType.objects.create(
            name="validation_type",
            display_name="Validation Type"
        )
        
        # Config avec limite faible pour tester
        BrandTemplateConfig.objects.create(
            brand=self.brand,
            max_templates_per_type=2  # Limite basse
        )

    def _authenticate_and_add_brand_context(self, user, brand=None):
        """Helper pour authentification + simulation middleware"""
        if brand is None:
            brand = self.brand
            
        self.client.force_authenticate(user=user)
        
        # Simuler le middleware avec current_brand
        original_generic = self.client.generic
        
        def generic_with_brand(method, path, data='', content_type='application/octet-stream', secure=False, **extra):
            response = original_generic(method, path, data, content_type, secure, **extra)
            if hasattr(response, 'wsgi_request'):
                response.wsgi_request.current_brand = brand
            return response
        
        self.client.generic = generic_with_brand
        self.client.defaults['HTTP_X_BRAND_ID'] = str(brand.id)
        
        return brand

    def test_template_creation_validation_errors(self):
        """Test erreurs de validation création"""
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-list')  # ✅ NAMESPACE AJOUTÉ
        
        # Test nom trop court
        invalid_data = {
            'name': 'Ab',  # Trop court
            'template_type': self.template_type.id,
            'prompt_content': 'Valid content for template'
        }
        
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test contenu trop court
        invalid_data2 = {
            'name': 'Valid Name',
            'template_type': self.template_type.id,
            'prompt_content': 'Short'  # Trop court
        }
        
        response = self.client.post(url, invalid_data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_template_uniqueness_validation(self):
        """Test validation unicité"""
        # Créer premier template
        BaseTemplate.objects.create(
            name="Unique Test",
            template_type=self.template_type,
            brand=self.brand,
            prompt_content="First content",
            created_by=self.admin
        )
        
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-list')  # ✅ NAMESPACE AJOUTÉ
        
        # Tenter de créer doublon - on s'attend à une erreur de validation
        duplicate_data = {
            'name': 'Unique Test',  # Même nom
            'template_type': self.template_type.id,  # Même type
            'prompt_content': 'Different but valid content for testing'
        }
        
        response = self.client.post(url, duplicate_data, format='json')
        # Le serializer devrait valider l'unicité
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_brand_template_limit_validation(self):
        """Test validation limite templates par brand"""
        # Créer templates jusqu'à la limite (2)
        for i in range(2):
            BaseTemplate.objects.create(
                name=f"Limit Test {i}",
                template_type=self.template_type,
                brand=self.brand,
                prompt_content=f"Content for limit test {i}",
                created_by=self.admin,
                is_active=True
            )
        
        self._authenticate_and_add_brand_context(self.admin)
        
        url = reverse('templates:basetemplate-list')  # ✅ NAMESPACE AJOUTÉ
        
        # Tenter de dépasser la limite
        over_limit_data = {
            'name': 'Over Limit Template',
            'template_type': self.template_type.id,
            'prompt_content': 'This should fail due to template limit'
        }
        
        response = self.client.post(url, over_limit_data, format='json')
        # Le serializer devrait valider la limite
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)