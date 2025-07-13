# 🧪 MEGAHUB - Standards & Règles Testing

## 📁 Organisation des Fichiers Tests

### **Structure par Système d'Apps**

```
# ✅ RÈGLE : Tests dans l'app PRINCIPALE de chaque système
onboarding_business/           # App principale du système onboarding
├── tests/                     # Tous les tests du système onboarding
│   ├── __init__.py
│   ├── factories.py           # Factories pour tout le système
│   ├── test_structure.py      # Tests architecture système
│   ├── test_business_endpoints.py      # Tests endpoints business
│   ├── test_invitations_endpoints.py  # Tests endpoints invitations
│   ├── test_trials_endpoints.py       # Tests endpoints trials
│   └── test_workflows.py      # Tests intégration complète
│
ai_core/                       # App principale du système AI
├── tests/
│   ├── factories.py           # Factories AI (AIJob, Provider, etc.)
│   ├── test_ai_endpoints.py   # Tests endpoints AI complets
│   └── test_ai_workflows.py   # Tests workflows IA
│
seo_websites_core/             # App principale du système SEO
├── tests/
│   ├── factories.py           # Factories SEO (Website, Page, etc.)
│   ├── test_websites_endpoints.py
│   └── test_seo_workflows.py
```

### **Apps Sans Système (Apps Individuelles)**

```
# ✅ RÈGLE : Tests dans l'app elle-même si pas de système
blog_content/                  # App individuelle
├── tests/
│   ├── factories.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
│
task_core/                     # App individuelle
├── tests/
│   ├── factories.py
│   └── test_endpoints.py
```

---

## 🔧 Conventions de Nommage

### **Fichiers Tests**

| Type | Nom | Description |
|------|-----|-------------|
| **Structure** | `test_structure.py` | Tests architecture & intégrité |
| **Endpoints** | `test_{system}_endpoints.py` | Tests API endpoints |
| **Workflows** | `test_{system}_workflows.py` | Tests intégration complète |
| **Models** | `test_models.py` | Tests models individuels |
| **Serializers** | `test_serializers.py` | Tests serializers individuels |
| **Services** | `test_services.py` | Tests services business |
| **Factories** | `factories.py` | Factory Boy factories |

### **Classes de Test**

```python
# ✅ CONVENTION : PascalCase + suffixe
class OnboardingBusinessEndpointsTest(APITestCase):
class UserInvitationModelTest(TestCase):  
class TrialWorkflowIntegrationTest(APITestCase):
class WebsiteFactoryTest(TestCase):
```

### **Méthodes de Test**

```python
# ✅ CONVENTION : test_ + action + context + expected
def test_create_business_when_user_registered_should_auto_setup(self):
def test_send_invitation_when_slots_full_should_raise_error(self):
def test_extend_trial_when_expired_should_fail(self):
def test_list_websites_when_brand_member_should_filter_accessible(self):
```

---

## 🏭 Factory Boy Standards

### **Organisation Factories**

```python
# factories.py - Une factory par modèle principal
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(DjangoModelFactory):
    """Factory pour CustomUser"""
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

class CompanyFactory(DjangoModelFactory):
    """Factory pour Company"""
    class Meta:
        model = 'company_core.Company'
    
    name = factory.Faker('company')
    admin = factory.SubFactory(UserFactory)
    billing_email = factory.LazyAttribute(lambda obj: obj.admin.email)

class BrandFactory(DjangoModelFactory):
    """Factory pour Brand"""
    class Meta:
        model = 'brands_core.Brand'
    
    name = factory.Faker('catch_phrase')
    company = factory.SubFactory(CompanyFactory)
    brand_admin = factory.SubFactory(UserFactory)
```

### **Traits et SubFactories**

```python
# ✅ TRAITS pour variations
class UserFactory(DjangoModelFactory):
    # ... base factory ...
    
    class Params:
        # Traits pour variations
        is_company_admin = factory.Trait(
            user_type='agency_admin'
        )
        is_brand_admin = factory.Trait(
            user_type='brand_admin'
        )
        with_company = factory.Trait(
            company=factory.SubFactory(CompanyFactory)
        )

# ✅ USAGE des traits
user_admin = UserFactory(is_company_admin=True, with_company=True)
brand_member = UserFactory(is_brand_admin=True)
```

---

## 🧪 Types de Tests & Responsabilités

### **1. Tests Structure (`test_structure.py`)**

```python
# ✅ OBJECTIF : Vérifier intégrité architecture
class OnboardingSystemStructureTest(TestCase):
    def test_all_onboarding_apps_in_installed_apps(self):
        """Vérifier que toutes les apps onboarding sont installées"""
    
    def test_signal_connections_active(self):
        """Vérifier que les signals sont connectés"""
    
    def test_url_patterns_complete(self):
        """Vérifier que tous les URL patterns sont configurés"""
```

### **2. Tests Endpoints (`test_{system}_endpoints.py`)**

```python
# ✅ OBJECTIF : Tester API endpoints complets
class OnboardingBusinessEndpointsTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_setup_status_returns_business_summary(self):
        """GET /onboarding/business/setup-status/"""
    
    def test_business_stats_requires_authentication(self):
        """GET /onboarding/business/stats/ sans auth → 401"""
```

### **3. Tests Workflows (`test_{system}_workflows.py`)**

```python
# ✅ OBJECTIF : Tester intégrations complètes
class OnboardingCompleteWorkflowTest(APITestCase):
    def test_complete_onboarding_flow(self):
        """User register → Business créé → Invitation → Accept → Upgrade"""
        # 1. User registration
        # 2. Auto business creation  
        # 3. Send invitation
        # 4. Accept invitation
        # 5. Add 2nd brand → auto upgrade
```

---

## ⚙️ Configuration Pytest

### **pytest.ini**

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = django_app.settings.test
python_files = tests.py test_*.py *_tests.py
python_classes = Test* *Test
python_functions = test_*
addopts = 
    --reuse-db
    --nomigrations
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --maxfail=5
    -v
testpaths = 
    onboarding_business/tests
    ai_core/tests  
    seo_websites_core/tests
```

### **settings/test.py**

```python
# settings/test.py - Configuration test dédiée
from .base import *

# Database en mémoire pour vitesse
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Désactiver migrations pour vitesse
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Celery synchrone pour tests
CELERY_TASK_ALWAYS_EAGER = True

# Email backend test
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

---

## 🚀 Commands Utiles

### **Lancer Tests**

```bash
# Tous les tests
pytest

# Tests d'un système
pytest onboarding_business/tests/

# Tests spécifiques  
pytest onboarding_business/tests/test_business_endpoints.py

# Tests avec couverture
pytest --cov=onboarding_business

# Tests parallèles (avec pytest-xdist)
pytest -n auto
```

### **Debug Tests**

```bash
# Mode verbose
pytest -v -s

# Arrêt au premier échec
pytest --maxfail=1

# PDB sur échec
pytest --pdb

# Profiling lenteur
pytest --durations=10
```

---

## 📊 Métriques & Couverture

### **Objectifs Couverture**

| Composant | Couverture Cible |
|-----------|------------------|
| **Models** | 95%+ |
| **Views/Endpoints** | 90%+ |
| **Services** | 95%+ |
| **Serializers** | 85%+ |
| **Factories** | 100% |

### **Exclusions Couverture**

```python
# .coveragerc
[run]
source = .
omit = 
    */migrations/*
    */venv/*
    manage.py
    */settings/*
    */tests/*
    */conftest.py
```

---

## 🔒 Sécurité & Données Test

### **Données Sensibles**

```python
# ✅ JAMAIS de vraies données en tests
class UserFactory(DjangoModelFactory):
    # ❌ MAL
    email = "real.user@realcompany.com"
    
    # ✅ BIEN  
    email = factory.Faker('email')
    api_key = factory.Faker('password', length=32)
```

### **Isolation Tests**

```python
# ✅ TOUJOURS utiliser transactions/rollback
class BaseTestCase(APITestCase):
    def setUp(self):
        # Chaque test = DB propre
        self.user = UserFactory()
    
    def tearDown(self):
        # Nettoyage automatique par Django TestCase
        pass
```

---

## 📝 Documentation Tests

### **Docstrings Obligatoires**

```python
def test_send_invitation_when_slots_full_should_raise_error(self):
    """
    Test que l'envoi d'invitation échoue quand slots pleins.
    
    Given: Company avec slots users pleins
    When: Tentative envoi invitation
    Then: ValidationError levée avec message explicite
    """
```

### **Comments Workflow**

```python
def test_complete_onboarding_workflow(self):
    """Test workflow onboarding complet"""
    # 1. GIVEN - Setup initial
    user = UserFactory()
    
    # 2. WHEN - Actions
    response = self.client.post('/onboarding/business/setup-status/')
    
    # 3. THEN - Assertions
    self.assertEqual(response.status_code, 200)
```

---

## 🎯 Standards Qualité

### **✅ Tests DOIVENT :**
- Être **isolés** (pas de dépendances entre tests)
- Être **rapides** (< 1s par test unitaire)
- Avoir **noms explicites** décrivant le comportement
- Tester **un seul concept** par test
- Utiliser **factories** pour données test
- Avoir **assertions précises**

### **❌ Tests NE DOIVENT PAS :**
- Dépendre de l'ordre d'exécution
- Utiliser `sleep()` ou timeouts
- Tester des détails d'implémentation
- Avoir de la logique complexe
- Partager des données entre tests
- Faire des appels réseau réels

---

**🏆 Ces standards garantissent des tests maintenables, rapides et fiables !**