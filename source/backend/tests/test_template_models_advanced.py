# backend/tests/test_template_models_advanced.py

import pytest
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from django.db import transaction

# Import des modèles à tester
from ai_templates_analytics.models import (
    TemplateUsageMetrics, TemplatePerformance, TemplatePopularity, TemplateFeedback
)
from ai_templates_insights.models import (
    TemplateRecommendation, TemplateInsight, OptimizationSuggestion, TrendAnalysis
)
from ai_templates_workflow.models import (
    TemplateValidationRule, TemplateValidationResult, TemplateApproval, TemplateReview
)
from seo_websites_ai_templates_content.models import (
    SEOWebsiteTemplate, SEOTemplateConfig, KeywordIntegrationRule, PageTypeTemplate
)

# Import des dépendances
from ai_templates_core.models import BaseTemplate, TemplateType
from ai_templates_categories.models import TemplateCategory
from brands_core.models import Brand, CustomUser


@pytest.fixture
def sample_brand():
    """Factory pour Brand"""
    return Brand.objects.create(
        name="Test Brand SEO",
        email="seo@testbrand.com"
    )


@pytest.fixture
def sample_user():
    """Factory pour CustomUser"""
    return CustomUser.objects.create_user(
        username="testuser_advanced",
        email="advanced@example.com",
        password="testpass123"
    )


@pytest.fixture
def template_type():
    """Factory pour TemplateType"""
    return TemplateType.objects.create(
        name="website",
        display_name="Website Templates"
    )


@pytest.fixture
def template_category():
    """Factory pour TemplateCategory"""
    return TemplateCategory.objects.create(
        name="seo",
        display_name="SEO Templates"
    )


@pytest.fixture
def base_template(sample_brand, template_type, sample_user):
    """Factory pour BaseTemplate"""
    return BaseTemplate.objects.create(
        name="SEO Landing Page",
        template_type=template_type,
        brand=sample_brand,
        prompt_content="Créez une landing page SEO pour {{brand_name}} avec {{target_keyword}}",
        created_by=sample_user
    )


# ===== TESTS ANALYTICS MODELS =====

@pytest.mark.django_db
class TestTemplateUsageMetricsModel:
    
    def test_usage_metrics_creation(self, base_template):
        """Test création TemplateUsageMetrics"""
        metrics = TemplateUsageMetrics.objects.create(
            template=base_template,
            total_uses=150,
            successful_generations=140,
            failed_generations=10,
            unique_users=75,
            avg_generation_time=2.5,
            popularity_score=8.7
        )
        
        assert metrics.template == base_template
        assert metrics.total_uses == 150
        assert metrics.successful_generations == 140
        assert metrics.failed_generations == 10
        assert metrics.unique_users == 75
        assert metrics.avg_generation_time == 2.5
        assert metrics.popularity_score == 8.7
    
    def test_usage_metrics_one_to_one_constraint(self, base_template):
        """Test contrainte OneToOne avec BaseTemplate"""
        TemplateUsageMetrics.objects.create(template=base_template)
        
        # Deuxième metrics pour même template devrait échouer
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                TemplateUsageMetrics.objects.create(template=base_template)
    
    def test_success_rate_property(self, base_template):
        """Test propriété success_rate calculée"""
        metrics = TemplateUsageMetrics.objects.create(
            template=base_template,
            total_uses=100,
            successful_generations=85,
            failed_generations=15
        )
        
        assert metrics.success_rate == 85.0
        
        # Test division par zéro
        metrics_zero = TemplateUsageMetrics.objects.create(
            template=BaseTemplate.objects.create(
                name="Empty Template",
                template_type=base_template.template_type,
                brand=base_template.brand,
                prompt_content="Empty"
            ),
            total_uses=0
        )
        
        assert metrics_zero.success_rate == 0
    
    def test_usage_metrics_str_method(self, base_template):
        """Test méthode __str__"""
        metrics = TemplateUsageMetrics.objects.create(
            template=base_template,
            total_uses=50
        )
        
        expected = f"Métriques {base_template.name}: 50 utilisations"
        assert str(metrics) == expected


@pytest.mark.django_db
class TestTemplatePerformanceModel:
    
    def test_performance_creation(self, base_template, sample_user):
        """Test création TemplatePerformance"""
        performance = TemplatePerformance.objects.create(
            template=base_template,
            user=sample_user,
            generation_time=1.8,
            tokens_used=250,
            output_quality_score=8.5,
            variables_used={"brand_name": "Test Brand", "target_keyword": "SEO"},
            was_successful=True
        )
        
        assert performance.template == base_template
        assert performance.user == sample_user
        assert performance.generation_time == 1.8
        assert performance.tokens_used == 250
        assert performance.output_quality_score == 8.5
        assert performance.variables_used == {"brand_name": "Test Brand", "target_keyword": "SEO"}
        assert performance.was_successful is True
        assert performance.error_message == ""
    
    def test_performance_with_error(self, base_template, sample_user):
        """Test performance avec erreur"""
        performance = TemplatePerformance.objects.create(
            template=base_template,
            user=sample_user,
            generation_time=0.5,
            was_successful=False,
            error_message="API timeout error"
        )
        
        assert performance.was_successful is False
        assert performance.error_message == "API timeout error"
    
    def test_performance_str_method(self, base_template, sample_user):
        """Test méthode __str__ avec emojis"""
        perf_success = TemplatePerformance.objects.create(
            template=base_template,
            user=sample_user,
            generation_time=2.1,
            was_successful=True
        )
        
        perf_failed = TemplatePerformance.objects.create(
            template=base_template,
            user=sample_user,
            generation_time=0.3,
            was_successful=False
        )
        
        assert str(perf_success) == f"✅ {base_template.name} - 2.1s"
        assert str(perf_failed) == f"❌ {base_template.name} - 0.3s"
    
    def test_performance_ordering(self, base_template, sample_user):
        """Test ordering par created_at décroissant"""
        perf1 = TemplatePerformance.objects.create(
            template=base_template, user=sample_user, generation_time=1.0
        )
        perf2 = TemplatePerformance.objects.create(
            template=base_template, user=sample_user, generation_time=2.0
        )
        
        performances = list(TemplatePerformance.objects.all())
        assert performances[0] == perf2  # Plus récent en premier
        assert performances[1] == perf1


@pytest.mark.django_db
class TestTemplatePopularityModel:
    
    def test_popularity_creation(self, base_template, template_category, sample_brand):
        """Test création TemplatePopularity"""
        today = date.today()
        popularity = TemplatePopularity.objects.create(
            template=base_template,
            category=template_category,
            brand=sample_brand,
            ranking_period="weekly",
            rank_position=3,
            usage_count=45,
            period_start=today - timedelta(days=7),
            period_end=today
        )
        
        assert popularity.template == base_template
        assert popularity.category == template_category
        assert popularity.brand == sample_brand
        assert popularity.ranking_period == "weekly"
        assert popularity.rank_position == 3
        assert popularity.usage_count == 45
    
    def test_popularity_unique_constraint(self, base_template, sample_brand):
        """Test contrainte unique_together"""
        today = date.today()
        
        TemplatePopularity.objects.create(
            template=base_template,
            brand=sample_brand,
            ranking_period="monthly",
            rank_position=1,
            usage_count=100,
            period_start=today.replace(day=1),
            period_end=today
        )
        
        # Même combinaison devrait échouer
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                TemplatePopularity.objects.create(
                    template=base_template,
                    brand=sample_brand,
                    ranking_period="monthly",
                    rank_position=2,  # Différent rank mais même clés uniques
                    usage_count=90,
                    period_start=today.replace(day=1),
                    period_end=today
                )
    
    def test_popularity_str_method(self, base_template, sample_brand):
        """Test méthode __str__"""
        today = date.today()
        popularity = TemplatePopularity.objects.create(
            template=base_template,
            brand=sample_brand,
            ranking_period="daily",
            rank_position=1,
            usage_count=50,
            period_start=today,
            period_end=today
        )
        
        expected = f"#1 {base_template.name} (daily)"
        assert str(popularity) == expected


@pytest.mark.django_db
class TestTemplateFeedbackModel:
    
    def test_feedback_creation(self, base_template, sample_user):
        """Test création TemplateFeedback"""
        feedback = TemplateFeedback.objects.create(
            template=base_template,
            user=sample_user,
            rating=4,
            comment="Très bon template, facile à utiliser",
            feedback_type="quality",
            is_public=True
        )
        
        assert feedback.template == base_template
        assert feedback.user == sample_user
        assert feedback.rating == 4
        assert feedback.comment == "Très bon template, facile à utiliser"
        assert feedback.feedback_type == "quality"
        assert feedback.is_public is True
        assert feedback.admin_response == ""
    
    def test_feedback_unique_constraint(self, base_template, sample_user):
        """Test contrainte unique_together template/user"""
        TemplateFeedback.objects.create(
            template=base_template,
            user=sample_user,
            rating=5,
            feedback_type="quality"
        )
        
        # Deuxième feedback du même user pour même template devrait échouer
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                TemplateFeedback.objects.create(
                    template=base_template,
                    user=sample_user,
                    rating=3,
                    feedback_type="bug_report"
                )
    
    def test_feedback_str_method(self, base_template, sample_user):
        """Test méthode __str__ avec emojis"""
        feedback = TemplateFeedback.objects.create(
            template=base_template,
            user=sample_user,
            rating=5,
            feedback_type="quality"
        )
        
        expected = f"5⭐ {base_template.name} par {sample_user.username}"
        assert str(feedback) == expected


# ===== TESTS INSIGHTS MODELS =====

@pytest.mark.django_db
class TestTemplateRecommendationModel:
    
    def test_recommendation_creation(self, sample_brand, sample_user, base_template):
        """Test création TemplateRecommendation"""
        recommendation = TemplateRecommendation.objects.create(
            brand=sample_brand,
            user=sample_user,
            recommended_template=base_template,
            recommendation_type="trending",
            confidence_score=0.85,
            reasoning="Template populaire dans votre secteur",
            priority=80
        )
        
        assert recommendation.brand == sample_brand
        assert recommendation.user == sample_user
        assert recommendation.recommended_template == base_template
        assert recommendation.recommendation_type == "trending"
        assert recommendation.confidence_score == 0.85
        assert recommendation.reasoning == "Template populaire dans votre secteur"
        assert recommendation.priority == 80
        assert recommendation.is_active is True
        assert recommendation.clicked is False
    
    def test_recommendation_without_user(self, sample_brand, base_template):
        """Test recommandation au niveau brand sans user spécifique"""
        recommendation = TemplateRecommendation.objects.create(
            brand=sample_brand,
            recommended_template=base_template,
            recommendation_type="performance_based",
            confidence_score=0.92,
            reasoning="Performance exceptionnelle",
            priority=95
        )
        
        assert recommendation.user is None
        assert recommendation.brand == sample_brand
    
    def test_recommendation_str_method(self, sample_brand, sample_user, base_template):
        """Test méthode __str__"""
        rec_with_user = TemplateRecommendation.objects.create(
            brand=sample_brand,
            user=sample_user,
            recommended_template=base_template,
            recommendation_type="trending",
            confidence_score=0.8,
            reasoning="Test"
        )
        
        rec_brand_only = TemplateRecommendation.objects.create(
            brand=sample_brand,
            recommended_template=base_template,
            recommendation_type="trending",
            confidence_score=0.8,
            reasoning="Test"
        )
        
        assert str(rec_with_user) == f"Rec: {base_template.name} → {sample_user.username}"
        assert str(rec_brand_only) == f"Rec: {base_template.name} → Brand {sample_brand.name}"


@pytest.mark.django_db
class TestTemplateInsightModel:
    
    def test_insight_creation(self, base_template):
        """Test création TemplateInsight"""
        insight = TemplateInsight.objects.create(
            template=base_template,
            insight_type="performance_drop",
            title="Baisse de performance détectée",
            description="Le taux de succès a chuté de 15% cette semaine",
            severity="medium",
            data_source={"success_rate_last_week": 85, "success_rate_this_week": 70}
        )
        
        assert insight.template == base_template
        assert insight.insight_type == "performance_drop"
        assert insight.title == "Baisse de performance détectée"
        assert insight.severity == "medium"
        assert insight.data_source == {"success_rate_last_week": 85, "success_rate_this_week": 70}
        assert insight.is_resolved is False
        assert insight.auto_generated is True
    
    def test_insight_str_method(self, base_template):
        """Test méthode __str__"""
        insight = TemplateInsight.objects.create(
            template=base_template,
            insight_type="critical",
            title="Problème critique détecté",
            description="Description",
            severity="critical"
        )
        
        assert str(insight) == "CRITICAL: Problème critique détecté"


@pytest.mark.django_db
class TestOptimizationSuggestionModel:
    
    def test_optimization_creation(self, base_template):
        """Test création OptimizationSuggestion"""
        suggestion = OptimizationSuggestion.objects.create(
            template=base_template,
            suggestion_type="content_improvement",
            title="Améliorer la structure H2",
            description="Ajouter plus de H2 pour améliorer la lisibilité",
            implementation_difficulty="easy",
            estimated_impact="medium",
            supporting_data={"current_h2_count": 2, "recommended_h2_count": 5}
        )
        
        assert suggestion.template == base_template
        assert suggestion.suggestion_type == "content_improvement"
        assert suggestion.title == "Améliorer la structure H2"
        assert suggestion.implementation_difficulty == "easy"
        assert suggestion.estimated_impact == "medium"
        assert suggestion.supporting_data == {"current_h2_count": 2, "recommended_h2_count": 5}
        assert suggestion.is_implemented is False
    
    def test_optimization_str_method(self, base_template):
        """Test méthode __str__"""
        suggestion = OptimizationSuggestion.objects.create(
            template=base_template,
            suggestion_type="seo_enhancement",
            title="Optimiser le maillage interne",
            description="Test",
            estimated_impact="high"
        )
        
        expected = "Optimiser le maillage interne (high impact)"
        assert str(suggestion) == expected


@pytest.mark.django_db
class TestTrendAnalysisModel:
    
    def test_trend_analysis_creation(self):
        """Test création TrendAnalysis"""
        today = date.today()
        analysis = TrendAnalysis.objects.create(
            analysis_type="usage_trends",
            scope="global",
            period_start=today - timedelta(days=30),
            period_end=today,
            trend_direction="increasing",
            trend_strength=0.75,
            key_findings={"growth_rate": 15, "top_category": "SEO"},
            visualization_data={"chart_type": "line", "data_points": [1, 2, 3, 4, 5]}
        )
        
        assert analysis.analysis_type == "usage_trends"
        assert analysis.scope == "global"
        assert analysis.trend_direction == "increasing"
        assert analysis.trend_strength == 0.75
        assert analysis.key_findings == {"growth_rate": 15, "top_category": "SEO"}
        assert analysis.visualization_data == {"chart_type": "line", "data_points": [1, 2, 3, 4, 5]}
    
    def test_trend_analysis_with_scope_id(self):
        """Test analyse avec scope_id pour brand spécifique"""
        today = date.today()
        analysis = TrendAnalysis.objects.create(
            analysis_type="performance_trends",
            scope="brand",
            scope_id=123,  # ID d'un brand spécifique
            period_start=today - timedelta(days=7),
            period_end=today,
            trend_direction="stable",
            trend_strength=0.1
        )
        
        assert analysis.scope == "brand"
        assert analysis.scope_id == 123
    
    def test_trend_str_method(self):
        """Test méthode __str__"""
        today = date.today()
        analysis = TrendAnalysis.objects.create(
            analysis_type="seasonal_patterns",
            scope="category",
            period_start=today - timedelta(days=365),
            period_end=today,
            trend_direction="volatile",
            trend_strength=0.8
        )
        
        expected = "seasonal_patterns (category) - volatile"
        assert str(analysis) == expected


# ===== TESTS WORKFLOW MODELS =====

class TestTemplateValidationRuleModel(TestCase):
    
    def test_validation_rule_creation(self):
        """Test création TemplateValidationRule"""
        rule = TemplateValidationRule.objects.create(
            name="security_check",
            description="Vérification des failles de sécurité",
            rule_type="security",
            validation_function="validate_security_content",
            is_blocking=True,
            error_message="Contenu potentiellement dangereux détecté"
        )
        
        assert rule.name == "security_check"
        assert rule.rule_type == "security"
        assert rule.validation_function == "validate_security_content"
        assert rule.is_active is True
        assert rule.is_blocking is True
        assert rule.error_message == "Contenu potentiellement dangereux détecté"
    
    def test_validation_rule_unique_name(self):
        """Test contrainte unique sur name"""
        TemplateValidationRule.objects.create(
            name="quality_check",
            rule_type="quality",
            validation_function="validate_quality"
        )
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                TemplateValidationRule.objects.create(
                    name="quality_check",
                    rule_type="format",
                    validation_function="validate_format"
                )
    
    def test_validation_rule_str_method(self):
        """Test méthode __str__"""
        rule = TemplateValidationRule.objects.create(
            name="format_validation",
            rule_type="format",
            validation_function="validate_format"
        )
        
        expected = "format_validation (format)"
        assert str(rule) == expected


@pytest.mark.django_db
class TestTemplateValidationResultModel:
    
    def test_validation_result_creation(self, base_template, sample_user):
        """Test création TemplateValidationResult"""
        rule = TemplateValidationRule.objects.create(
            name="content_check",
            rule_type="content",
            validation_function="validate_content"
        )
        
        result = TemplateValidationResult.objects.create(
            template=base_template,
            validation_rule=rule,
            is_valid=True,
            validated_by=sample_user,
            validation_data={"word_count": 150, "readability_score": 8.5}
        )
        
        assert result.template == base_template
        assert result.validation_rule == rule
        assert result.is_valid is True
        assert result.validated_by == sample_user
        assert result.validation_data == {"word_count": 150, "readability_score": 8.5}
        assert result.error_details == ""
    
    def test_validation_result_with_error(self, base_template):
        """Test résultat avec erreur"""
        rule = TemplateValidationRule.objects.create(
            name="security_check",
            rule_type="security",
            validation_function="validate_security"
        )
        
        result = TemplateValidationResult.objects.create(
            template=base_template,
            validation_rule=rule,
            is_valid=False,
            error_details="Script potentiellement malveillant détecté ligne 15"
        )
        
        assert result.is_valid is False
        assert result.error_details == "Script potentiellement malveillant détecté ligne 15"
    
    def test_validation_result_str_method(self, base_template):
        """Test méthode __str__ avec emojis"""
        rule = TemplateValidationRule.objects.create(
            name="quality_check",
            rule_type="quality",
            validation_function="validate_quality"
        )
        
        result_valid = TemplateValidationResult.objects.create(
            template=base_template,
            validation_rule=rule,
            is_valid=True
        )
        
        result_invalid = TemplateValidationResult.objects.create(
            template=base_template,
            validation_rule=rule,
            is_valid=False
        )
        
        assert str(result_valid) == f"✅ {base_template.name} - quality_check"
        assert str(result_invalid) == f"❌ {base_template.name} - quality_check"


@pytest.mark.django_db
class TestTemplateApprovalModel:
    
    def test_approval_creation(self, base_template, sample_user):
        """Test création TemplateApproval"""
        approval = TemplateApproval.objects.create(
            template=base_template,
            status="pending_review",
            submitted_by=sample_user,
            submitted_at=timezone.now()
        )
        
        assert approval.template == base_template
        assert approval.status == "pending_review"
        assert approval.submitted_by == sample_user
        assert approval.submitted_at is not None
        assert approval.reviewed_by is None
        assert approval.reviewed_at is None
    
    def test_approval_with_review(self, base_template, sample_user):
        """Test approval avec review et rejet"""
        reviewer = CustomUser.objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="pass123"
        )
        
        approval = TemplateApproval.objects.create(
            template=base_template,
            status="rejected",
            submitted_by=sample_user,
            reviewed_by=reviewer,
            reviewed_at=timezone.now(),
            rejection_reason="Template ne respecte pas les guidelines de contenu"
        )
        
        assert approval.status == "rejected"
        assert approval.reviewed_by == reviewer
        assert approval.reviewed_at is not None
        assert approval.rejection_reason == "Template ne respecte pas les guidelines de contenu"
    
    def test_approval_str_method(self, base_template):
        """Test méthode __str__"""
        approval = TemplateApproval.objects.create(
            template=base_template,
            status="approved"
        )
        
        expected = f"{base_template.name} - approved"
        assert str(approval) == expected


@pytest.mark.django_db
class TestTemplateReviewModel:
    
    def test_review_creation(self, base_template, sample_user):
        """Test création TemplateReview"""
        approval = TemplateApproval.objects.create(
            template=base_template,
            status="pending_review"
        )
        
        review = TemplateReview.objects.create(
            approval=approval,
            reviewer=sample_user,
            comment="Template de bonne qualité, quelques ajustements mineurs à faire",
            rating=4,
            review_type="suggestion"
        )
        
        assert review.approval == approval
        assert review.reviewer == sample_user
        assert review.comment == "Template de bonne qualité, quelques ajustements mineurs à faire"
        assert review.rating == 4
        assert review.review_type == "suggestion"
    
    def test_review_str_method(self, base_template, sample_user):
        """Test méthode __str__"""
        approval = TemplateApproval.objects.create(
            template=base_template,
            status="pending_review"
        )
        
        review = TemplateReview.objects.create(
            approval=approval,
            reviewer=sample_user,
            comment="Excellent travail",
            review_type="approval"
        )
        
        expected = f"Review {base_template.name} par {sample_user.username}"
        assert str(review) == expected


# ===== TESTS SEO MODELS =====

@pytest.mark.django_db
class TestSEOWebsiteTemplateModel:
    
    def test_seo_template_creation(self, base_template, template_category):
        """Test création SEOWebsiteTemplate"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            category=template_category,
            page_type="landing",
            search_intent="TOFU",
            target_word_count=1200,
            keyword_density_target=2.1
        )
        
        assert seo_template.base_template == base_template
        assert seo_template.category == template_category
        assert seo_template.page_type == "landing"
        assert seo_template.search_intent == "TOFU"
        assert seo_template.target_word_count == 1200
        assert seo_template.keyword_density_target == 2.1
    
    def test_seo_template_one_to_one_constraint(self, base_template):
        """Test contrainte OneToOne avec BaseTemplate"""
        SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="landing"
        )
        
        # Deuxième SEO config pour même base template devrait échouer
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                SEOWebsiteTemplate.objects.create(
                    base_template=base_template,
                    page_type="vitrine"
                )
    
    def test_seo_template_str_method(self, base_template):
        """Test méthode __str__"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="service"
        )
        
        expected = f"SEO: {base_template.name} (service)"
        assert str(seo_template) == expected


@pytest.mark.django_db
class TestSEOTemplateConfigModel:
    
    def test_seo_config_creation(self, base_template):
        """Test création SEOTemplateConfig"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="produit"
        )
        
        config = SEOTemplateConfig.objects.create(
            seo_template=seo_template,
            h1_structure="{{target_keyword}} - Meilleur {{product_type}} | {{brand_name}}",
            h2_pattern="## Pourquoi choisir {{brand_name}} pour {{target_keyword}}?",
            meta_title_template="{{target_keyword}} | {{brand_name}} - {{year}}",
            meta_description_template="Découvrez {{target_keyword}} chez {{brand_name}}. {{value_proposition}}",
            internal_linking_rules={"min_links": 3, "max_links": 8, "prefer_deep_pages": True},
            schema_markup_type="Product"
        )
        
        assert config.seo_template == seo_template
        assert "{{target_keyword}}" in config.h1_structure
        assert "{{brand_name}}" in config.meta_title_template
        assert config.internal_linking_rules == {"min_links": 3, "max_links": 8, "prefer_deep_pages": True}
        assert config.schema_markup_type == "Product"
    
    def test_seo_config_defaults(self, base_template):
        """Test valeurs par défaut SEOTemplateConfig"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="blog"
        )
        
        config = SEOTemplateConfig.objects.create(seo_template=seo_template)
        
        assert config.h1_structure == "{{target_keyword}} - {{brand_name}}"
        assert config.h2_pattern == "## {{secondary_keyword}}\n\n{{content_section}}"
        assert config.meta_title_template == "{{target_keyword}} | {{brand_name}}"
        assert "{{description_intro}}" in config.meta_description_template
    
    def test_seo_config_str_method(self, base_template):
        """Test méthode __str__"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="category"
        )
        
        config = SEOTemplateConfig.objects.create(seo_template=seo_template)
        
        expected = f"Config SEO: {base_template.name}"
        assert str(config) == expected


@pytest.mark.django_db
class TestKeywordIntegrationRuleModel:
    
    def test_keyword_rule_creation(self, base_template):
        """Test création KeywordIntegrationRule"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="landing"
        )
        
        rule = KeywordIntegrationRule.objects.create(
            seo_template=seo_template,
            keyword_type="primary",
            placement_rules={
                "h1_required": True,
                "h2_min": 2,
                "paragraph_frequency": "every_3rd",
                "alt_text": True
            },
            density_min=1.0,
            density_max=2.5,
            natural_variations=True
        )
        
        assert rule.seo_template == seo_template
        assert rule.keyword_type == "primary"
        assert rule.placement_rules["h1_required"] is True
        assert rule.placement_rules["h2_min"] == 2
        assert rule.density_min == 1.0
        assert rule.density_max == 2.5
        assert rule.natural_variations is True
    
    def test_keyword_rule_unique_constraint(self, base_template):
        """Test contrainte unique_together seo_template/keyword_type"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="service"
        )
        
        KeywordIntegrationRule.objects.create(
            seo_template=seo_template,
            keyword_type="secondary",
            density_min=0.5,
            density_max=1.5
        )
        
        # Même combinaison devrait échouer
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                KeywordIntegrationRule.objects.create(
                    seo_template=seo_template,
                    keyword_type="secondary",
                    density_min=1.0,
                    density_max=2.0
                )
    
    def test_keyword_rule_str_method(self, base_template):
        """Test méthode __str__"""
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            page_type="vitrine"
        )
        
        rule = KeywordIntegrationRule.objects.create(
            seo_template=seo_template,
            keyword_type="anchor"
        )
        
        expected = f"{base_template.name} - anchor"
        assert str(rule) == expected


class TestPageTypeTemplateModel(TestCase):
    
    def test_page_type_template_creation(self):
        """Test création PageTypeTemplate"""
        template = PageTypeTemplate.objects.create(
            name="Landing Page Standard",
            page_type="landing",
            template_structure="""
            # {{h1_title}}
            
            ## {{value_proposition}}
            {{intro_paragraph}}
            
            ## Bénéfices
            {{benefits_list}}
            
            ## Call-to-Action
            {{cta_section}}
            """,
            default_sections=["hero", "benefits", "social_proof", "cta"],
            required_variables=["h1_title", "value_proposition", "brand_name"]
        )
        
        assert template.name == "Landing Page Standard"
        assert template.page_type == "landing"
        assert "{{h1_title}}" in template.template_structure
        assert template.default_sections == ["hero", "benefits", "social_proof", "cta"]
        assert template.required_variables == ["h1_title", "value_proposition", "brand_name"]
        assert template.is_active is True
    
    def test_page_type_unique_constraint(self):
        """Test contrainte unique_together name/page_type"""
        PageTypeTemplate.objects.create(
            name="Template Pro",
            page_type="service",
            template_structure="Content"
        )
        
        # Même nom + même page_type devrait échouer
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                PageTypeTemplate.objects.create(
                    name="Template Pro",
                    page_type="service",
                    template_structure="Different content"
                )
        
        # Mais même nom + page_type différent devrait passer
        PageTypeTemplate.objects.create(
            name="Template Pro",
            page_type="produit",
            template_structure="Product content"
        )
    
    def test_page_type_str_method(self):
        """Test méthode __str__"""
        template = PageTypeTemplate.objects.create(
            name="Blog Article Template",
            page_type="blog",
            template_structure="# {{title}}\n{{content}}"
        )
        
        expected = "Blog Article Template (blog)"
        assert str(template) == expected


# ===== TESTS D'INTÉGRATION AVANCÉS =====

@pytest.mark.django_db
class TestAdvancedModelIntegration:
    
    def test_complete_seo_template_setup(self, sample_brand, sample_user, template_category):
        """Test setup complet d'un template SEO avec toutes ses relations"""
        # Template de base
        template_type = TemplateType.objects.create(name="website", display_name="Website")
        base_template = BaseTemplate.objects.create(
            name="Landing SEO Pro",
            template_type=template_type,
            brand=sample_brand,
            prompt_content="Créez une landing page SEO optimisée",
            created_by=sample_user
        )
        
        # Configuration SEO
        seo_template = SEOWebsiteTemplate.objects.create(
            base_template=base_template,
            category=template_category,
            page_type="landing",
            search_intent="BOFU",
            target_word_count=1500
        )
        
        # Configuration avancée
        seo_config = SEOTemplateConfig.objects.create(
            seo_template=seo_template,
            schema_markup_type="Service"
        )
        
        # Règles de mots-clés
        primary_rule = KeywordIntegrationRule.objects.create(
            seo_template=seo_template,
            keyword_type="primary",
            density_min=1.5,
            density_max=3.0
        )
        
        secondary_rule = KeywordIntegrationRule.objects.create(
            seo_template=seo_template,
            keyword_type="secondary",
            density_min=0.5,
            density_max=1.5
        )
        
        # Métriques
        metrics = TemplateUsageMetrics.objects.create(
            template=base_template,
            total_uses=250,
            successful_generations=230
        )
        
        # Vérifications des relations
        assert seo_template.base_template == base_template
        assert seo_config.seo_template == seo_template
        assert primary_rule.seo_template == seo_template
        assert secondary_rule.seo_template == seo_template
        assert metrics.template == base_template
        
        # Relations reverse
        assert hasattr(base_template, 'seo_config')
        assert base_template.seo_config == seo_template
        assert seo_template.keyword_rules.count() == 2
        assert base_template.usage_metrics == metrics
    
    def test_workflow_approval_complete_cycle(self, sample_brand, sample_user):
        """Test cycle complet d'approbation avec validations"""
        # Template
        template_type = TemplateType.objects.create(name="email", display_name="Email")
        template = BaseTemplate.objects.create(
            name="Newsletter Template",
            template_type=template_type,
            brand=sample_brand,
            prompt_content="Créez une newsletter engageante",
            created_by=sample_user
        )
        
        # Règles de validation
        security_rule = TemplateValidationRule.objects.create(
            name="security_scan",
            rule_type="security",
            validation_function="scan_malicious_content",
            is_blocking=True
        )
        
        quality_rule = TemplateValidationRule.objects.create(
            name="quality_check",
            rule_type="quality",
            validation_function="check_content_quality",
            is_blocking=False
        )
        
        # Résultats de validation
        security_result = TemplateValidationResult.objects.create(
            template=template,
            validation_rule=security_rule,
            is_valid=True,
            validated_by=sample_user
        )
        
        quality_result = TemplateValidationResult.objects.create(
            template=template,
            validation_rule=quality_rule,
            is_valid=False,
            error_details="Score de lisibilité trop bas"
        )
        
        # Processus d'approbation
        approval = TemplateApproval.objects.create(
            template=template,
            status="pending_review",
            submitted_by=sample_user,
            submitted_at=timezone.now()
        )
        
        # Review
        reviewer = CustomUser.objects.create_user(
            username="reviewer_advanced",
            email="reviewer_adv@example.com",
            password="pass123"
        )
        
        review = TemplateReview.objects.create(
            approval=approval,
            reviewer=reviewer,
            comment="Template fonctionnel mais améliorer la qualité",
            rating=3,
            review_type="suggestion"
        )
        
        # Vérifications
        assert template.validation_results.count() == 2
        assert template.approvals.count() == 1
        assert approval.reviews.count() == 1
        assert security_result.is_valid is True
        assert quality_result.is_valid is False
        assert review.approval == approval
    
    def test_analytics_and_insights_integration(self, sample_brand, sample_user):
        """Test intégration complète analytics et insights"""
        # Template de base
        template_type = TemplateType.objects.create(name="social", display_name="Social Media")
        template = BaseTemplate.objects.create(
            name="Instagram Post Template",
            template_type=template_type,
            brand=sample_brand,
            prompt_content="Créez un post Instagram engageant",
            created_by=sample_user
        )
        
        # Métriques d'usage
        metrics = TemplateUsageMetrics.objects.create(
            template=template,
            total_uses=500,
            successful_generations=450,
            failed_generations=50,
            unique_users=125,
            avg_generation_time=1.8,
            popularity_score=9.2
        )
        
        # Performances détaillées
        perf1 = TemplatePerformance.objects.create(
            template=template,
            user=sample_user,
            generation_time=1.5,
            tokens_used=180,
            output_quality_score=8.5,
            was_successful=True
        )
        
        perf2 = TemplatePerformance.objects.create(
            template=template,
            user=sample_user,
            generation_time=0.8,
            was_successful=False,
            error_message="Rate limit exceeded"
        )
        
        # Feedback utilisateur
        feedback = TemplateFeedback.objects.create(
            template=template,
            user=sample_user,
            rating=5,
            comment="Template parfait pour mes posts Instagram",
            feedback_type="quality",
            is_public=True
        )
        
        # Insights automatiques
        insight = TemplateInsight.objects.create(
            template=template,
            insight_type="trending_up",
            title="Template en forte croissance",
            description="Utilisation en hausse de 45% ce mois",
            severity="low",
            data_source={"growth_rate": 45, "period": "monthly"}
        )
        
        # Recommandation
        recommendation = TemplateRecommendation.objects.create(
            brand=sample_brand,
            user=sample_user,
            recommended_template=template,
            recommendation_type="trending",
            confidence_score=0.95,
            reasoning="Template très populaire dans votre secteur"
        )
        
        # Vérifications des relations
        assert template.usage_metrics == metrics
        assert template.performance_logs.count() == 2
        assert template.feedback.count() == 1
        assert template.insights.count() == 1
        
        # Test propriétés calculées
        assert metrics.success_rate == 90.0  # 450/500 * 100
        
        # Relations reverse
        assert perf1 in template.performance_logs.all()
        assert perf2 in template.performance_logs.all()
        assert feedback in template.feedback.all()
        assert insight in template.insights.all()
        assert recommendation.recommended_template == template


if __name__ == "__main__":
    pytest.main([__file__, "-v"])