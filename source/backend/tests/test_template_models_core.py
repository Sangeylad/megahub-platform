# backend/tests/test_template_models_core.py

import pytest
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

# Import des modèles à tester
from ai_templates_categories.models import TemplateCategory, TemplateTag, CategoryPermission
from ai_templates_core.models import TemplateType, BrandTemplateConfig, BaseTemplate
from ai_templates_storage.models import TemplateVariable, TemplateVersion

# Assumons ces modèles business (ou on peut mocker)
from brands_core.models import Brand, CustomUser

User = get_user_model()

@pytest.fixture
def sample_brand():
    """Factory pour Brand"""
    return Brand.objects.create(
        name="Test Brand",
        email="test@testbrand.com"
    )

@pytest.fixture
def sample_user():
    """Factory pour CustomUser"""
    return CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def template_type():
    """Factory pour TemplateType"""
    return TemplateType.objects.create(
        name="website",
        display_name="Website Templates",
        description="Templates pour sites web"
    )

@pytest.fixture
def root_category():
    """Factory pour catégorie racine"""
    return TemplateCategory.objects.create(
        name="marketing",
        display_name="Marketing",
        description="Templates marketing"
    )


class TestTemplateCategoryModel(TestCase):
    
    def setUp(self):
        self.root_category = TemplateCategory.objects.create(
            name="marketing",
            display_name="Marketing",
            description="Templates marketing"
        )
    
    def test_template_category_creation(self):
        """Test création basique TemplateCategory"""
        category = TemplateCategory.objects.create(
            name="seo",
            display_name="SEO Templates",
            description="Templates SEO"
        )
        
        assert category.name == "seo"
        assert category.display_name == "SEO Templates"
        assert category.level == 1  # Niveau par défaut
        assert category.is_active is True
        assert category.created_at is not None
        assert category.updated_at is not None
    
    def test_category_hierarchy_level_auto_calculation(self):
        """Test calcul automatique du niveau hiérarchique"""
        # Catégorie enfant
        child_category = TemplateCategory.objects.create(
            name="landing",
            display_name="Landing Pages",
            parent=self.root_category
        )
        
        assert child_category.level == 2
        assert child_category.parent == self.root_category
        
        # Petit-enfant
        grandchild = TemplateCategory.objects.create(
            name="conversion",
            display_name="Conversion Pages",
            parent=child_category
        )
        
        assert grandchild.level == 3
    
    def test_category_unique_constraint(self):
        """Test contrainte d'unicité parent/name"""
        # Première catégorie
        TemplateCategory.objects.create(
            name="seo",
            display_name="SEO",
            parent=self.root_category
        )
        
        # Duplicate sous même parent devrait échouer
        with pytest.raises(IntegrityError):
            TemplateCategory.objects.create(
                name="seo",
                display_name="SEO Duplicate",
                parent=self.root_category
            )
    
    def test_category_str_method(self):
        """Test méthode __str__ avec indentation"""
        child = TemplateCategory.objects.create(
            name="seo",
            display_name="SEO Templates",
            parent=self.root_category
        )
        
        assert str(self.root_category) == "Marketing"
        assert str(child) == "→ SEO Templates"

    def test_category_ordering(self):
        """Test ordering par level, sort_order, name"""
        # On supprime self.root_category pour ce test ou on l'utilise
        cat1 = TemplateCategory.objects.create(
            name="z_last",
            display_name="Z Last", 
            sort_order=10
        )
        
        cat2 = TemplateCategory.objects.create(
            name="a_first",
            display_name="A First",
            sort_order=5  
        )
        
        # On prend seulement les 2 qu'on vient de créer
        categories = list(TemplateCategory.objects.filter(name__in=["z_last", "a_first"]).order_by('level', 'sort_order', 'name'))
        
        assert categories[0] == cat2  # sort_order=5
        assert categories[1] == cat1  # sort_order=10

class TestTemplateTagModel(TestCase):
    
    def test_template_tag_creation(self):
        """Test création TemplateTag"""
        tag = TemplateTag.objects.create(
            name="conversion",
            display_name="Conversion",
            description="Templates axés conversion",
            color="green"
        )
        
        assert tag.name == "conversion"
        assert tag.color == "green"
        assert tag.usage_count == 0
        assert tag.is_active is True
    
    def test_tag_unique_name_constraint(self):
        """Test contrainte d'unicité sur name"""
        TemplateTag.objects.create(name="seo", display_name="SEO")
        
        with pytest.raises(IntegrityError):
            TemplateTag.objects.create(name="seo", display_name="SEO Duplicate")
    
    def test_tag_ordering(self):
        """Test ordering par usage_count décroissant"""
        tag1 = TemplateTag.objects.create(name="popular", display_name="Popular", usage_count=100)
        tag2 = TemplateTag.objects.create(name="medium", display_name="Medium", usage_count=50)
        tag3 = TemplateTag.objects.create(name="new", display_name="New", usage_count=0)
        
        tags = list(TemplateTag.objects.all())
        assert tags[0] == tag1  # Plus utilisé
        assert tags[1] == tag2
        assert tags[2] == tag3


class TestCategoryPermissionModel(TestCase):
    
    def setUp(self):
        self.category = TemplateCategory.objects.create(
            name="premium",
            display_name="Premium Templates"
        )
    
    def test_category_permission_creation(self):
        """Test création CategoryPermission"""
        permission = CategoryPermission.objects.create(
            category=self.category,
            permission_type="create",
            required_plan="pro"
        )
        
        assert permission.category == self.category
        assert permission.permission_type == "create"
        assert permission.required_plan == "pro"
        assert permission.is_active is True
    
    def test_permission_unique_constraint(self):
        """Test contrainte unique_together"""
        CategoryPermission.objects.create(
            category=self.category,
            permission_type="create",
            required_plan="pro"
        )
        
        # Même combinaison devrait échouer
        with pytest.raises(IntegrityError):
            CategoryPermission.objects.create(
                category=self.category,
                permission_type="create",
                required_plan="pro"
            )


class TestTemplateTypeModel(TestCase):
    
    def test_template_type_creation(self):
        """Test création TemplateType"""
        template_type = TemplateType.objects.create(
            name="email",
            display_name="Email Templates",
            description="Templates pour emails"
        )
        
        assert template_type.name == "email"
        assert template_type.is_active is True
    
    def test_template_type_unique_name(self):
        """Test contrainte unique sur name"""
        TemplateType.objects.create(name="website", display_name="Website")
        
        with pytest.raises(IntegrityError):
            TemplateType.objects.create(name="website", display_name="Website Duplicate")


@pytest.mark.django_db
class TestBrandTemplateConfigModel:
    
    def test_brand_template_config_creation(self, sample_brand):
        """Test création BrandTemplateConfig"""
        config = BrandTemplateConfig.objects.create(
            brand=sample_brand,
            max_templates_per_type=100,
            max_variables_per_template=30
        )
        
        assert config.brand == sample_brand
        assert config.max_templates_per_type == 100
        assert config.allow_custom_templates is True
        assert config.default_template_style == "professional"
    
    def test_brand_config_one_to_one_constraint(self, sample_brand):
        """Test contrainte OneToOne avec Brand"""
        BrandTemplateConfig.objects.create(brand=sample_brand)
        
        # Deuxième config pour même brand devrait échouer
        with pytest.raises(IntegrityError):
            BrandTemplateConfig.objects.create(brand=sample_brand)


@pytest.mark.django_db
class TestBaseTemplateModel:
    
    def test_base_template_creation(self, sample_brand, sample_user, template_type):
        """Test création BaseTemplate"""
        template = BaseTemplate.objects.create(
            name="Landing Page Pro",
            description="Template landing page professionnel",
            template_type=template_type,
            brand=sample_brand,
            prompt_content="Créez une landing page pour {{brand_name}} ciblant {{target_keyword}}",
            created_by=sample_user
        )
        
        assert template.name == "Landing Page Pro"
        assert template.template_type == template_type
        assert template.brand == sample_brand
        assert template.is_active is True
        assert template.is_public is False
        assert "{{brand_name}}" in template.prompt_content
    
    def test_template_unique_constraint(self, sample_brand, template_type):
        """Test contrainte unique_together brand/name/template_type"""
        BaseTemplate.objects.create(
            name="SEO Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Test content"
        )
        
        # Même combinaison devrait échouer
        with pytest.raises(IntegrityError):
            BaseTemplate.objects.create(
                name="SEO Template",
                brand=sample_brand,
                template_type=template_type,
                prompt_content="Different content"
            )
    
    def test_template_str_method(self, sample_brand, template_type):
        """Test méthode __str__"""
        template = BaseTemplate.objects.create(
            name="Test Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Test"
        )
        
        expected = f"Test Template ({template_type.display_name})"
        assert str(template) == expected


class TestTemplateVariableModel(TestCase):
    
    def test_template_variable_creation(self):
        """Test création TemplateVariable"""
        variable = TemplateVariable.objects.create(
            name="brand_name",
            display_name="Nom de la marque",
            description="Le nom officiel de la marque",
            variable_type="brand",
            default_value="Mon Entreprise",
            is_required=True
        )
        
        assert variable.name == "brand_name"
        assert variable.variable_type == "brand"
        assert variable.is_required is True
    
    def test_variable_unique_name_constraint(self):
        """Test contrainte unique sur name"""
        TemplateVariable.objects.create(name="keyword", display_name="Keyword")
        
        with pytest.raises(IntegrityError):
            TemplateVariable.objects.create(name="keyword", display_name="Keyword 2")
    
    def test_variable_str_method(self):
        """Test méthode __str__ avec accolades"""
        variable = TemplateVariable.objects.create(
            name="target_keyword",
            display_name="Mot-clé cible"
        )
        
        assert str(variable) == "{{target_keyword}}"


@pytest.mark.django_db
class TestTemplateVersionModel:
    
    def test_template_version_creation(self, sample_brand, sample_user, template_type):
        """Test création TemplateVersion"""
        template = BaseTemplate.objects.create(
            name="Test Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Version 1 content"
        )
        
        version = TemplateVersion.objects.create(
            template=template,
            prompt_content="Version 1 content",
            changelog="Version initiale",
            is_current=True,
            created_by=sample_user
        )
        
        assert version.template == template
        assert version.version_number == 1  # Auto-incrémenté
        assert version.is_current is True
    
    def test_version_auto_increment(self, sample_brand, template_type):
        """Test auto-incrémentation version_number"""
        template = BaseTemplate.objects.create(
            name="Test Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Content"
        )
        
        # Version 1
        v1 = TemplateVersion.objects.create(
            template=template,
            prompt_content="V1 content"
        )
        assert v1.version_number == 1
        
        # Version 2
        v2 = TemplateVersion.objects.create(
            template=template,
            prompt_content="V2 content"
        )
        assert v2.version_number == 2
        
        # Version 3
        v3 = TemplateVersion.objects.create(
            template=template,
            prompt_content="V3 content"
        )
        assert v3.version_number == 3
    
    def test_version_unique_constraint(self, sample_brand, template_type):
        """Test contrainte unique_together template/version_number"""
        template = BaseTemplate.objects.create(
            name="Test Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Content"
        )
        
        TemplateVersion.objects.create(
            template=template,
            version_number=1,
            prompt_content="V1"
        )
        
        # Même version_number devrait échouer
        with pytest.raises(IntegrityError):
            TemplateVersion.objects.create(
                template=template,
                version_number=1,
                prompt_content="V1 duplicate"
            )
    
    def test_version_str_method(self, sample_brand, template_type):
        """Test méthode __str__"""
        template = BaseTemplate.objects.create(
            name="SEO Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Content"
        )
        
        version = TemplateVersion.objects.create(
            template=template,
            prompt_content="V2 content"
        )
        
        assert str(version) == "SEO Template v2"
    
    def test_version_ordering(self, sample_brand, template_type):
        """Test ordering par version_number décroissant"""
        template = BaseTemplate.objects.create(
            name="Test Template",
            brand=sample_brand,
            template_type=template_type,
            prompt_content="Content"
        )
        
        v1 = TemplateVersion.objects.create(template=template, prompt_content="V1")
        v2 = TemplateVersion.objects.create(template=template, prompt_content="V2")
        v3 = TemplateVersion.objects.create(template=template, prompt_content="V3")
        
        versions = list(TemplateVersion.objects.all())
        assert versions[0] == v3  # Plus récent en premier
        assert versions[1] == v2
        assert versions[2] == v1


# Tests d'intégration pour relations entre modèles
@pytest.mark.django_db
class TestModelRelationshipsIntegration:
    
    def test_category_hierarchy_relationships(self):
        """Test relations hiérarchiques complètes"""
        root = TemplateCategory.objects.create(name="marketing", display_name="Marketing")
        child1 = TemplateCategory.objects.create(name="seo", display_name="SEO", parent=root)
        child2 = TemplateCategory.objects.create(name="social", display_name="Social", parent=root)
        grandchild = TemplateCategory.objects.create(name="facebook", display_name="Facebook", parent=child2)
        
        # Test relations directes
        assert child1.parent == root
        assert grandchild.parent == child2
        
        # Test relations reverse
        children = root.children.all()
        assert child1 in children
        assert child2 in children
        assert grandchild not in children  # Pas enfant direct
        
        # Test cascade delete
        child2.delete()
        assert not TemplateCategory.objects.filter(pk=grandchild.pk).exists()
    
    def test_template_with_full_relations(self, sample_brand, sample_user):
        """Test template avec toutes ses relations"""
        # Setup
        template_type = TemplateType.objects.create(name="website", display_name="Website")
        category = TemplateCategory.objects.create(name="landing", display_name="Landing")
        
        # Template
        template = BaseTemplate.objects.create(
            name="Premium Landing",
            template_type=template_type,
            brand=sample_brand,
            prompt_content="Content with {{brand_name}}",
            created_by=sample_user
        )
        
        # Variables
        var1 = TemplateVariable.objects.create(name="brand_name", display_name="Brand Name")
        var2 = TemplateVariable.objects.create(name="keyword", display_name="Keyword")
        
        # Versions
        v1 = TemplateVersion.objects.create(template=template, prompt_content="V1", created_by=sample_user)
        v2 = TemplateVersion.objects.create(template=template, prompt_content="V2", created_by=sample_user)
        
        # Vérifications des relations
        assert template.versions.count() == 2
        assert v1 in template.versions.all()
        assert v2 in template.versions.all()
        
        # Test reverse relations
        assert template in sample_brand.ai_templates.all()
        assert template in sample_user.authored_ai_templates.all()
        assert v1 in sample_user.authored_template_versions.all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])