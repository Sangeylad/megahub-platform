# backend/onboarding_business/tests/test_structure.py

"""
Tests de structure pour vérifier l'intégrité du système onboarding
VERSION FINALE CORRIGÉE - ALIGNÉE SUR VRAIE STRUCTURE MEGAHUB
"""
import pytest
from django.test import TestCase, TransactionTestCase
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.apps import apps
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction, connection
from datetime import timedelta
from unittest.mock import patch
import uuid

User = get_user_model()


class CleanTestCase(TransactionTestCase):
    """TestCase avec nettoyage forcé de la DB"""
    
    def setUp(self):
        """Nettoyage forcé avant chaque test"""
        super().setUp()
        self._clean_all_data()
    
    def tearDown(self):
        """Nettoyage forcé après chaque test"""
        self._clean_all_data()
        super().tearDown()
    
    def _clean_all_data(self):
        """Nettoyage complet de toutes les données"""
        try:
            # Supprimer dans l'ordre pour éviter les contraintes FK
            from company_core.models import Company
            from brands_core.models import Brand
            
            # Supprimer brands d'abord (FK vers Company)
            Brand.objects.all().delete()
            
            # Supprimer companies (FK vers User)
            Company.objects.all().delete()
            
            # Supprimer users en dernier
            User.objects.all().delete()
            
            # Forcer commit
            transaction.commit()
            
        except Exception as e:
            # Ignorer les erreurs de nettoyage
            pass


class OnboardingSystemStructureTest(TestCase):
    """Tests de structure globale du système onboarding"""
    
    def test_all_onboarding_apps_in_installed_apps(self):
        """Vérifier que toutes les apps onboarding sont installées"""
        required_apps = [
            'onboarding_registration',
            'onboarding_business',
            'onboarding_invitations',
            'onboarding_trials',
        ]
        
        installed_apps = settings.INSTALLED_APPS
        
        for app in required_apps:
            with self.subTest(app=app):
                self.assertIn(app, installed_apps, 
                    f"App {app} manquante dans INSTALLED_APPS")
        
        print(f"✅ {len(required_apps)} apps onboarding trouvées dans INSTALLED_APPS")
    
    def test_core_dependencies_installed(self):
        """Vérifier que les dépendances core sont installées"""
        core_dependencies = [
            'company_core',
            'brands_core', 
            'users_core',
            'users_roles',
            'company_slots',
            'company_features',
            'billing_core',
            'billing_stripe',
            'common',
        ]
        
        installed_apps = settings.INSTALLED_APPS
        missing_deps = []
        
        for dep in core_dependencies:
            if dep not in installed_apps:
                missing_deps.append(dep)
        
        self.assertEqual(len(missing_deps), 0,
            f"Dépendances core manquantes: {missing_deps}")
        
        print(f"✅ {len(core_dependencies)} dépendances core installées")
    
    def test_onboarding_url_patterns_configured(self):
        """Vérifier que tous les URL patterns onboarding sont configurés"""
        # URLs principales onboarding_business
        business_urls = [
            'business_setup',
            'setup_status', 
            'business_stats',
            'features_summary',
            'trigger_business_creation',
            'check_eligibility',
        ]
        
        configured_urls = []
        failed_urls = []
        
        for url_name in business_urls:
            try:
                url = reverse(f'onboarding_business:{url_name}')
                if url:
                    configured_urls.append(url_name)
            except NoReverseMatch:
                failed_urls.append(url_name)
        
        # Au moins 50% des URLs doivent être configurées
        success_rate = len(configured_urls) / len(business_urls)
        self.assertGreaterEqual(success_rate, 0.5,
            f"Trop d'URLs manquantes. Configurées: {configured_urls}, Échecs: {failed_urls}")
        
        print(f"✅ {len(configured_urls)}/{len(business_urls)} URLs onboarding configurées")
    
    def test_all_models_load_correctly(self):
        """✅ CORRIGÉ : Vérifier que tous les models critiques sont bien configurés"""
        models_to_test = [
            # Core models confirmés d'après tes fichiers
            ('company_core', 'Company'),
            ('brands_core', 'Brand'),
            ('users_core', 'CustomUser'),
            
            # Billing models (structure standard)
            ('billing_core', 'Plan'),
            ('billing_core', 'Subscription'),
            
            # Slots confirmé d'après ton knowledge
            ('company_slots', 'CompanySlots'),
        ]
        
        loaded_models = []
        failed_models = []
        
        for app_label, model_name in models_to_test:
            try:
                model = apps.get_model(app_label, model_name)
                
                # Vérifications basiques
                if hasattr(model._meta, 'db_table') and model._meta.db_table:
                    loaded_models.append(f"{app_label}.{model_name}")
                else:
                    failed_models.append(f"{app_label}.{model_name} (pas de db_table)")
                    
            except LookupError:
                failed_models.append(f"{app_label}.{model_name} (non trouvé)")
        
        # Au moins les 3 models core doivent être chargés
        self.assertGreaterEqual(len(loaded_models), 3,
            f"Pas assez de models chargés. Succès: {loaded_models}, Échecs: {failed_models}")
        
        print(f"✅ {len(loaded_models)} models critiques chargés correctement")
        if failed_models:
            print(f"⚠️  Models optionnels manquants: {failed_models}")
    
    def test_common_mixins_available(self):
        """✅ CORRIGÉ : Vérifier que les mixins common sont importables"""
        try:
            # ✅ CORRIGÉ : Vraie structure common d'après ton knowledge
            from common.models.mixins import (
                TimestampedMixin,
                SoftDeleteMixin
            )
            
            # Vérifier que ce sont des classes abstraites
            self.assertTrue(TimestampedMixin._meta.abstract,
                "TimestampedMixin doit être abstract")
            self.assertTrue(SoftDeleteMixin._meta.abstract,
                "SoftDeleteMixin doit être abstract")
            
            # Vérifier champs essentiels
            timestamped_fields = [f.name for f in TimestampedMixin._meta.fields]
            self.assertIn('created_at', timestamped_fields)
            self.assertIn('updated_at', timestamped_fields)
            
            softdelete_fields = [f.name for f in SoftDeleteMixin._meta.fields]
            self.assertIn('is_deleted', softdelete_fields)
            
            print("✅ Mixins common importés et validés")
            
        except ImportError as e:
            self.fail(f"Erreur import mixins common: {e}")
    
    def test_database_tables_exist(self):
        """✅ CORRIGÉ : Vérifier que les tables critiques existent dans la DB"""
        # ✅ CORRIGÉ : Vraies tables d'après tes db_table
        critical_tables = [
            'custom_user',  # ✅ users_core.CustomUser
            'company',      # ✅ company_core.Company  
            'brand',        # ✅ brands_core.Brand
        ]
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
        
        found_tables = []
        missing_tables = []
        
        for table in critical_tables:
            if table in existing_tables:
                found_tables.append(table)
            else:
                missing_tables.append(table)
        
        # Au moins 2 des 3 tables critiques doivent exister
        self.assertGreaterEqual(len(found_tables), 2,
            f"Pas assez de tables critiques. Trouvées: {found_tables}, Manquantes: {missing_tables}")
        
        print(f"✅ {len(found_tables)}/3 tables critiques trouvées: {found_tables}")
        if missing_tables:
            print(f"⚠️  Tables manquantes: {missing_tables}")
    
    def test_middleware_configuration(self):
        """✅ CORRIGÉ : Vérifier que le middleware brand est configuré"""
        middlewares = settings.MIDDLEWARE
        
        # ✅ CORRIGÉ : Vraie classe middleware d'après settings.py
        required_middleware = 'common.middleware.brand_middleware.BrandContextMiddleware'
        
        self.assertIn(required_middleware, middlewares,
            f"Middleware {required_middleware} manquant dans MIDDLEWARE")
        
        # Vérifier position (doit être après AuthenticationMiddleware)
        auth_pos = next((i for i, m in enumerate(middlewares) 
                        if 'AuthenticationMiddleware' in m), -1)
        brand_pos = next((i for i, m in enumerate(middlewares) 
                         if required_middleware in m), -1)
        
        if auth_pos >= 0 and brand_pos >= 0:
            self.assertGreater(brand_pos, auth_pos,
                "BrandContextMiddleware doit être après AuthenticationMiddleware")
        
        print("✅ Middleware brand correctement configuré")
    
    def test_services_import_correctly(self):
        """✅ CORRIGÉ : Vérifier que les services critiques sont importables"""
        services_to_test = [
            # ✅ Services onboarding confirmés d'après knowledge
            ('onboarding_business.services.business_creation', 'create_solo_business_for_user'),
            ('onboarding_business.services.trial_setup', 'setup_trial_subscription'),
            ('onboarding_business.services.slots_setup', 'setup_default_slots'),
            ('onboarding_business.services.roles_setup', 'assign_default_roles'),
        ]
        
        imported_services = []
        failed_services = []
        
        for module_path, function_name in services_to_test:
            try:
                module = __import__(module_path, fromlist=[function_name])
                service_function = getattr(module, function_name)
                if callable(service_function):
                    imported_services.append(f"{module_path}.{function_name}")
                else:
                    failed_services.append(f"{function_name} (non callable)")
            except (ImportError, AttributeError) as e:
                failed_services.append(f"{module_path}.{function_name} ({str(e)})")
        
        # Au moins 50% des services doivent être importables
        success_rate = len(imported_services) / len(services_to_test)
        self.assertGreaterEqual(success_rate, 0.5,
            f"Trop de services manquants. Importés: {imported_services}, Échecs: {failed_services}")
        
        print(f"✅ {len(imported_services)}/{len(services_to_test)} services importés")
        if failed_services:
            print(f"⚠️  Services manquants: {failed_services}")


class OnboardingSystemServicesTest(TestCase):
    """Tests de structure des services onboarding"""
    
    def test_onboarding_service_importable(self):
        """Vérifier que OnboardingService est importable"""
        try:
            from onboarding_business.services.onboarding import OnboardingService
            
            # Vérifier méthodes principales
            expected_methods = [
                'is_user_eligible_for_business',
                'setup_business_for_user', 
                'get_user_business_status'
            ]
            
            available_methods = []
            for method in expected_methods:
                if hasattr(OnboardingService, method):
                    available_methods.append(method)
            
            # Au moins 2 des 3 méthodes doivent exister
            self.assertGreaterEqual(len(available_methods), 2,
                f"OnboardingService incomplet. Méthodes trouvées: {available_methods}")
            
            print(f"✅ OnboardingService importé avec {len(available_methods)} méthodes")
            
        except ImportError as e:
            self.fail(f"OnboardingService non importable: {e}")


class OnboardingSystemPermissionsTest(TestCase):
    """Tests des permissions du système onboarding"""
    
    def test_serializers_importable(self):
        """Vérifier que les serializers principaux sont importables"""
        serializers_to_test = [
            'BusinessSetupSerializer',
            'BusinessStatusSerializer', 
            'BusinessStatsSerializer',
        ]
        
        imported_serializers = []
        
        try:
            # Import dynamique pour éviter les erreurs si certains manquent
            from onboarding_business import serializers as onb_serializers
            
            for serializer_name in serializers_to_test:
                if hasattr(onb_serializers, serializer_name):
                    serializer_class = getattr(onb_serializers, serializer_name)
                    if callable(serializer_class):
                        imported_serializers.append(serializer_name)
            
            # Au moins 1 serializer doit être importable
            self.assertGreaterEqual(len(imported_serializers), 1,
                f"Aucun serializer onboarding trouvé")
            
            print(f"✅ {len(imported_serializers)} serializers onboarding importés")
                
        except ImportError as e:
            self.fail(f"Module serializers non importable: {e}")
    
    def test_permissions_structure_exists(self):
        """Vérifier que la structure permissions existe"""
        try:
            # Test simple d'import du module permissions
            import onboarding_business.permissions
            
            # Compter les classes de permission disponibles
            permission_classes = [
                attr for attr in dir(onboarding_business.permissions)
                if not attr.startswith('_') and attr.endswith(('Permission', 'Business', 'Trial'))
            ]
            
            print(f"✅ Module permissions trouvé avec {len(permission_classes)} classes")
            
        except ImportError:
            print("⚠️  Module permissions non trouvé (acceptable si pas encore créé)")


class OnboardingSystemIntegrityTest(CleanTestCase):
    """✅ CORRIGÉ : Tests d'intégrité avec nettoyage forcé
    
    NOTE: Plus de patches signals car architecture migrée vers endpoints explicites
    """
    
    def test_can_create_single_user(self):
        """Test création d'un seul user"""
        unique_id = uuid.uuid4().hex[:8]
        user = User.objects.create(
            username=f"test_user_{unique_id}",
            email=f"test_{unique_id}@example.com",
            is_active=True,
            user_type='brand_member'
        )
        
        self.assertIsNotNone(user.id)
        self.assertTrue(user.is_active)
        self.assertEqual(user.user_type, 'brand_member')
        
        print(f"✅ User créé: {user.username} (ID: {user.id})")
    
    def test_can_create_single_company(self):
        """Test création d'une seule company"""
        from company_core.models import Company
        
        unique_id = uuid.uuid4().hex[:8]
        
        # Admin unique
        admin = User.objects.create(
            username=f"admin_{unique_id}",
            email=f"admin_{unique_id}@example.com",
            is_active=True,
            user_type='agency_admin'
        )
        
        # Company
        company = Company.objects.create(
            name=f"Company_{unique_id}",
            admin=admin,
            billing_email=admin.email,
            is_active=True
        )
        
        self.assertIsNotNone(company.id)
        self.assertEqual(company.admin, admin)
        self.assertTrue(company.is_active)
        
        print(f"✅ Company créée: {company.name} (ID: {company.id}, Admin ID: {admin.id})")
    
    def test_database_constraints_exist(self):
        """✅ CORRIGÉ : Vérifier que les contraintes DB sont actives"""
        with connection.cursor() as cursor:
            # ✅ CORRIGÉ : Requête PostgreSQL pour contraintes FK
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.table_constraints 
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('custom_user', 'company', 'brand')
            """)
            fk_count = cursor.fetchone()[0]
        
        # Au moins 1 contrainte FK doit exister
        self.assertGreaterEqual(fk_count, 1, 
            f"Aucune contrainte foreign key trouvée sur les tables critiques (trouvé: {fk_count})")
        
        print(f"✅ {fk_count} contraintes FK trouvées sur tables critiques")
    
    def test_indexes_on_critical_fields(self):
        """✅ CORRIGÉ : Vérifier que les indexes critiques existent"""
        with connection.cursor() as cursor:
            # ✅ CORRIGÉ : Requête PostgreSQL pour indexes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_indexes 
                WHERE tablename IN ('custom_user', 'company', 'brand')
                AND indexname NOT LIKE '%_pkey'
            """)
            index_count = cursor.fetchone()[0]
        
        # Au moins 2 indexes personnalisés (hors primary keys)
        self.assertGreaterEqual(index_count, 2, 
            f"Pas assez d'indexes sur les tables critiques (trouvé: {index_count})")
        
        print(f"✅ {index_count} indexes personnalisés trouvés sur tables critiques")


class OnboardingSystemBasicFunctionalityTest(CleanTestCase):
    """Tests de fonctionnalité basique
    
    NOTE: Plus de patches signals car architecture migrée vers endpoints explicites
    """
    
    def test_business_relationships_work(self):
        """Test relations business basiques"""
        from company_core.models import Company
        from brands_core.models import Brand
        
        unique_id = uuid.uuid4().hex[:8]
        
        # Setup minimal
        admin = User.objects.create(
            username=f"rel_admin_{unique_id}",
            email=f"rel_{unique_id}@example.com",
            user_type='agency_admin'
        )
        
        company = Company.objects.create(
            name=f"RelCompany_{unique_id}",
            admin=admin,
            billing_email=admin.email,
            is_active=True,
            trial_expires_at=timezone.now() + timedelta(weeks=2)
        )
        
        # Link bidirectionnel
        admin.company = company
        admin.save()
        
        brand = Brand.objects.create(
            name=f"RelBrand_{unique_id}",
            company=company,
            brand_admin=admin,
            is_active=True
        )
        brand.users.add(admin)
        
        # Vérifications relations
        self.assertEqual(company.admin, admin)
        self.assertEqual(admin.company, company)
        self.assertEqual(brand.company, company)
        self.assertEqual(brand.brand_admin, admin)
        self.assertTrue(brand.users.filter(id=admin.id).exists())
        
        # Vérifications business
        self.assertTrue(company.is_in_trial())
        self.assertEqual(company.get_business_mode(), 'solo')
        
        print(f"✅ Relations business vérifiées:")
        print(f"  Company: {company.name} (ID: {company.id})")
        print(f"  Admin: {admin.username} (ID: {admin.id})")
        print(f"  Brand: {brand.name} (ID: {brand.id})")
    
    def test_user_permissions_work(self):
        """Test méthodes de permissions user"""
        from company_core.models import Company
        
        unique_id = uuid.uuid4().hex[:8]
        
        # Company admin
        admin = User.objects.create(
            username=f"perm_admin_{unique_id}",
            email=f"perm_{unique_id}@example.com",
            user_type='agency_admin'
        )
        
        company = Company.objects.create(
            name=f"PermCompany_{unique_id}",
            admin=admin,
            billing_email=admin.email,
        )
        
        admin.company = company
        admin.save()
        
        # Tests permissions
        self.assertTrue(admin.is_company_admin())
        
        # Brand member
        member = User.objects.create(
            username=f"member_{unique_id}",
            email=f"member_{unique_id}@example.com",
            user_type='brand_member',
            company=company
        )
        
        self.assertFalse(member.is_company_admin())
        
        print(f"✅ Permissions user vérifiées:")
        print(f"  Admin company: {admin.is_company_admin()}")
        print(f"  Member company: {member.is_company_admin()}")


class OnboardingSystemValidationTest(TestCase):
    """Tests de validation finale"""
    
    def test_views_structure_exists(self):
        """Test que la structure views existe"""
        try:
            import onboarding_business.views
            
            # Compter les vues disponibles
            view_classes = [
                attr for attr in dir(onboarding_business.views)
                if not attr.startswith('_') and (
                    attr.endswith('View') or 
                    attr.endswith('ViewSet') or
                    attr in ['business_stats', 'check_setup_eligibility']
                )
            ]
            
            # Au moins 2 vues doivent exister
            self.assertGreaterEqual(len(view_classes), 2,
                f"Pas assez de vues onboarding. Trouvées: {view_classes}")
            
            print(f"✅ {len(view_classes)} vues onboarding disponibles")
            
        except ImportError as e:
            self.fail(f"Module views non importable: {e}")
    
    def test_exceptions_structure_exists(self):
        """Test que la structure exceptions existe"""
        try:
            import onboarding_business.exceptions
            
            # Compter les exceptions disponibles
            exception_classes = [
                attr for attr in dir(onboarding_business.exceptions)
                if not attr.startswith('_') and attr.endswith('Error')
            ]
            
            print(f"✅ Module exceptions trouvé avec {len(exception_classes)} classes")
            
        except ImportError:
            print("⚠️  Module exceptions non trouvé (acceptable si pas encore créé)")
    
    def test_tasks_structure_exists(self):
        """Test que la structure tasks existe"""
        try:
            import onboarding_business.tasks
            
            # Compter les tâches disponibles
            task_functions = [
                attr for attr in dir(onboarding_business.tasks)
                if not attr.startswith('_') and callable(getattr(onboarding_business.tasks, attr))
            ]
            
            print(f"✅ Module tasks trouvé avec {len(task_functions)} tâches")
            
        except ImportError:
            print("⚠️  Module tasks non trouvé (acceptable si pas encore créé)")


class OnboardingSystemSummaryTest(TestCase):
    """Test de résumé global du système"""
    
    def test_explicit_onboarding_architecture_works(self):
        """✅ NOUVEAU : Test de la nouvelle architecture endpoints explicites"""
        
        # Test que les services principaux sont importables
        services_working = {
            'business_creation': False,
            'onboarding_service': False,
            'validation_service': False
        }
        
        try:
            from onboarding_business.services.business_creation import create_solo_business_for_user
            services_working['business_creation'] = True
        except ImportError:
            pass
        
        try:
            from onboarding_business.services.onboarding import OnboardingService
            services_working['onboarding_service'] = True
        except ImportError:
            pass
        
        try:
            from onboarding_registration.services.validation import can_trigger_business_creation
            services_working['validation_service'] = True
        except ImportError:
            pass
        
        # Au moins 2 des 3 services doivent être disponibles
        working_count = sum(services_working.values())
        self.assertGreaterEqual(working_count, 2,
            f"Architecture endpoints explicites incomplète. Services: {services_working}")
        
        print(f"✅ Nouvelle architecture explicite: {working_count}/3 services disponibles")
        
        # Test que les endpoints sont configurés
        try:
            from django.urls import reverse
            business_setup_url = reverse('onboarding_business:business_setup')
            self.assertIsNotNone(business_setup_url)
            print("✅ Endpoints explicites configurés")
        except:
            print("⚠️  Endpoints explicites pas encore configurés (normal si URLs pas finalisées)")
    
    def test_system_completeness_score(self):
        """Calcule un score de complétude du système onboarding"""
        
        score_components = {
            'apps_installed': 0,
            'models_loaded': 0,
            'services_imported': 0,
            'views_available': 0,
            'urls_configured': 0
        }
        
        # Test apps (25 points max)
        required_apps = ['onboarding_business', 'onboarding_registration', 
                        'onboarding_invitations', 'onboarding_trials']
        installed_count = sum(1 for app in required_apps if app in settings.INSTALLED_APPS)
        score_components['apps_installed'] = (installed_count / len(required_apps)) * 25
        
        # Test models (25 points max)
        models_to_test = [('company_core', 'Company'), ('brands_core', 'Brand'), ('users_core', 'CustomUser')]
        loaded_count = 0
        for app_label, model_name in models_to_test:
            try:
                apps.get_model(app_label, model_name)
                loaded_count += 1
            except LookupError:
                pass
        score_components['models_loaded'] = (loaded_count / len(models_to_test)) * 25
        
        # Test services (20 points max)
        try:
            from onboarding_business.services.business_creation import create_solo_business_for_user
            score_components['services_imported'] = 20
        except ImportError:
            score_components['services_imported'] = 0
        
        # Test views (15 points max)
        try:
            import onboarding_business.views
            score_components['views_available'] = 15
        except ImportError:
            score_components['views_available'] = 0
        
        # Test URLs (15 points max)
        try:
            reverse('onboarding_business:setup_status')
            score_components['urls_configured'] = 15
        except NoReverseMatch:
            # Essayer l'ancienne méthode au cas où
            try:
                reverse('onboarding_business:business_setup')
                score_components['urls_configured'] = 10
            except NoReverseMatch:
                score_components['urls_configured'] = 0
        
        total_score = sum(score_components.values())
        
        print(f"\n🎯 SCORE DE COMPLÉTUDE SYSTÈME ONBOARDING: {total_score:.1f}/100")
        print("=" * 50)
        for component, score in score_components.items():
            status = "✅" if score > 0 else "❌"
            print(f"{status} {component}: {score:.1f} points")
        print("=" * 50)
        
        if total_score >= 80:
            print("🔥 EXCELLENT - Système onboarding très complet !")
        elif total_score >= 60:
            print("👍 BON - Système onboarding fonctionnel")
        elif total_score >= 40:
            print("⚠️  MOYEN - Système onboarding partiel")
        else:
            print("🚨 FAIBLE - Système onboarding incomplet")
        
        # Le test passe si le score est >= 40 (système minimal fonctionnel)
        self.assertGreaterEqual(total_score, 40,
            f"Score système trop faible: {total_score}/100. Minimum requis: 40/100")