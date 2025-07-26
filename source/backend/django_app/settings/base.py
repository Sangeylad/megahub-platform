# /var/www/megahub/source/backend/django_app/settings/base.py
# ✅ VERSION CORRIGÉE - STATICFILES_DIRS Fix

from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-rn*s%lh@cq2tm0!%66=*a+*j-2irr(x!&&wrj-jhk#0x#)8nuq')

# Application definition - TES 50+ APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_celery_beat', 
    'django_celery_results', 
    'file_converter',
    'public_tools',
    'file_compressor',
    'glossary.apps.GlossaryConfig',
    'common',
    'blog_content',
    'blog_editor',
    'blog_publishing',
    'blog_config',
    'blog_collections',
    'seo_keywords_base',
    'seo_keywords_metrics', 
    'seo_keywords_cocoons',
    'seo_keywords_ppa',
    'seo_keywords_content_types',
    'seo_websites_core',
    'seo_websites_categorization',
    'seo_pages_content',
    'seo_pages_hierarchy',
    'seo_pages_layout',
    'seo_pages_workflow',
    'seo_pages_seo',
    'seo_pages_keywords',
    'task_core',
    'task_persistence',
    'task_monitoring',
    'task_scheduling',
    'ai_core',
    'ai_openai',
    'ai_providers',
    'ai_usage',
    'django_extensions',
    'brands_design_colors',
    'brands_design_typography', 
    'brands_design_spacing',
    'brands_design_tailwind',
    'ai_templates_core',
    'ai_templates_storage',
    'ai_templates_categories',
    'seo_websites_ai_templates_content',
    'ai_templates_workflow',
    'ai_templates_analytics', 
    'ai_templates_insights',
    'company_core',
    'company_slots',
    'company_features',
    'brands_core',
    'users_core',
    'users_roles',
    'billing_core',
    'billing_stripe',
    'onboarding_registration',
    'onboarding_business', 
    'onboarding_invitations',
    'onboarding_trials',
    'auth_core',
    'company_categorization_core',        # Catégories core
    'company_categorization_fintech',     # Profils FinTech  
    'company_categorization_saas',        # Profils SaaS
    'company_categorization_realestate',  # Profils Immobilier
    'company_categorization_healthcare',  # Profils Santé
    'company_categorization_ecommerce',   # Profils E-commerce
    'company_categorization_services',    # Profils Services Pro
    'crm_entities_core',        # Entités principales (Account, Contact, Opportunity)
    'crm_entities_relations',   # Relations entre entités
    'crm_entities_scoring',     # Scoring et analytics
    'crm_entities_enrichment',  # Enrichissement données
    'crm_pipeline_core',         # Pipeline et Stage core
    'crm_pipeline_automation',   # Automatisation rules
    'crm_pipeline_forecasting',  # Prévisions commerciales
    'crm_activities_core',             # Activités de base
    'crm_activities_communication',    # Call, Email, Meeting
    'crm_activities_tasks',           # Task, Reminder
    'crm_activities_notes',           # Note, Comment
    'crm_workflow_core',         # Workflow, WorkflowStep, Execution
    'crm_workflow_automation',   # Triggers, Conditions, Actions
    'crm_workflow_templates',    # Templates & Presets sectoriels
    'crm_analytics_core',         # Dashboard, Metric, Chart
    'crm_analytics_reports',      # Report, Generation, Filter
    'crm_analytics_forecasting',  # Forecast, Scenario, Trend
    'crm_analytics_kpis',         # KPI, Performance, Benchmark
    'crm_analytics_predictions',  # Prediction, Recommendation, Insight
    'crm_analytics_sentiment',    # Sentiment, TextAnalysis, Profile
    'mailing_contacts_core',
    'mailing_contacts_preferences',
    'mailing_contacts_tracking',
    'mailing_contacts_lifecycle',
    'mailing_campaigns_core',
    'mailing_campaigns_sending',
    'mailing_templates_core',
    'mailing_templates_versions',
    'mailing_lists_core',
    'mailing_lists_segments',
    'mailing_lists_imports',
    'mailing_lists_compliance',
    'mailing_analytics_core',
    'mailing_analytics_opens',
    'mailing_analytics_clicks',
    'mailing_analytics_conversions',
    'mailing_analytics_reports',
    'mailing_automations_core',
    'mailing_automations_triggers',
    'mailing_automations_actions',
    'mailing_automations_conditions',
    'mailing_automations_sequences',
    'mailing_deliverability_core',
    'mailing_deliverability_warming',
    'mailing_deliverability_monitoring',
    'mailing_deliverability_bounces',
    'mailing_deliverability_authentication',
    'mailing_deliverability_reputation',
    'mailing_integrations_core',
    'mailing_integrations_crm',
    'mailing_integrations_api',
    'mailing_integrations_forms',
    'mailing_configuration_core',
    'mailing_configuration_domains',
    'mailing_configuration_users',
    'mailing_configuration_branding',
    'mailing_configuration_limits',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middleware.brand_middleware.BrandContextMiddleware',
]

# Configuration file_converter
FILE_CONVERTER_CONFIG = {
    'MAX_FILE_SIZE': 50 * 1024 * 1024,
    'DEFAULT_MONTHLY_LIMIT': 100,
    'FILE_RETENTION_HOURS': 24,
    'SUPPORTED_FORMATS': {
        'document': ['docx', 'doc', 'odt', 'pdf', 'txt', 'md', 'html'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
        'spreadsheet': ['xlsx', 'xls', 'csv', 'ods'],
        'presentation': ['pptx', 'ppt', 'odp']
    }
}

FILE_CONVERTER_STORAGE_ROOT = os.path.join(BASE_DIR, 'storage', 'file_conversions')

# Configuration public tools
PUBLIC_TOOLS_CONFIG = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,
    'FILE_RETENTION_HOURS': 1,
    'HOURLY_LIMIT_PER_IP': 100,
    'DAILY_LIMIT_PER_IP': 500,
    'ALLOWED_FORMATS': {
        'input': ['pdf', 'docx', 'doc', 'txt', 'md', 'html'],
        'output': ['pdf', 'docx', 'txt', 'md', 'html']
    },
    'BLOCKED_USER_AGENTS': [
        'bot', 'crawler', 'spider', 'scraper',
        'automated', 'python-requests', 'curl', 'wget'
    ],
    'WORDPRESS_DOMAINS': [
        'https://humari.fr',
        'https://www.humari.fr',
    ]
}

PUBLIC_TOOLS_STORAGE_ROOT = os.path.join(BASE_DIR, 'storage', 'public_conversions')

ROOT_URLCONF = 'django_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'public_tools', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_app.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ✅ STATIC FILES CONFIGURATION - CORRIGÉE
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# ✅ STATIC_ROOT pour collectstatic (obligatoire staging/production)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ✅ STATICFILES_DIRS - Seulement si dossier existe
STATICFILES_DIRS = []  # Vide par défaut - évite le warning

# Vérifier existence du dossier static avant de l'ajouter
STATIC_DIR = os.path.join(BASE_DIR, 'static')
if os.path.exists(STATIC_DIR):
    STATICFILES_DIRS.append(STATIC_DIR)

# Configuration staticfiles - Optimisations production
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Storage pour production (avec compression)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users_core.CustomUser' 

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '10000/day',
        'public_tools_anon': '200/hour',
        'public_tools_process': '100/hour',
        'glossary_read': '1000/hour',
        'glossary_search': '300/hour',
        'glossary_stats': '100/hour',
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Storage
OPENAI_STORAGE_ROOT = os.path.join(BASE_DIR, 'storage', 'openai_exports')

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

CELERY_TASK_TIME_LIMIT = 6000
CELERY_TASK_SOFT_TIME_LIMIT = 5400

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-conversions': {
        'task': 'file_converter.tasks.cleanup_expired_conversions',
        'schedule': crontab(hour=2, minute=0),
    },
    'reset-monthly-quotas': {
        'task': 'file_converter.tasks.reset_monthly_quotas',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
    'cleanup-public-conversions': {
        'task': 'public_tools.tasks.cleanup_public_conversions',
        'schedule': crontab(minute=0),
    },
    'reset-hourly-quotas': {
        'task': 'public_tools.tasks.reset_hourly_quotas', 
        'schedule': crontab(minute=0),
    },
    'cleanup-old-quotas': {
        'task': 'public_tools.tasks.cleanup_old_quotas',
        'schedule': crontab(hour=3, minute=0),
    },
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'public_tools': {
            'format': '[PUBLIC] {levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'public_tools_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'public_tools.log'),
            'formatter': 'public_tools',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'public_tools': {
            'handlers': ['public_tools_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'public_tools.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'file_converter': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Créer les dossiers de logs
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Génération clé AI
AI_ENCRYPTION_KEY = os.environ.get('AI_ENCRYPTION_KEY')
if not AI_ENCRYPTION_KEY:
    try:
        from cryptography.fernet import Fernet
        AI_ENCRYPTION_KEY = Fernet.generate_key().decode()
        print(f"🔑 AI_ENCRYPTION_KEY générée: {AI_ENCRYPTION_KEY[:10]}...")
    except ImportError:
        import secrets
        import base64
        key_bytes = secrets.token_bytes(32)
        AI_ENCRYPTION_KEY = base64.urlsafe_b64encode(key_bytes).decode()