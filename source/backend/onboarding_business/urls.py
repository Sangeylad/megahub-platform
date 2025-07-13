# backend/onboarding_business/urls.py

from django.urls import path
from . import views

app_name = 'onboarding_business'

urlpatterns = [
    # ====== SETUP BUSINESS EXPLICITE (OPTION A) ======
    # Endpoint principal pour setup business
    path('setup/', views.BusinessSetupView.as_view(), name='business_setup'),
    
    # Status d'onboarding complet
    path('setup-status/', views.BusinessSetupStatusView.as_view(), name='setup_status'),
    
    # Vérification éligibilité (avant setup)
    path('check-eligibility/', views.check_setup_eligibility, name='check_eligibility'),
    
    # ====== BUSINESS STATS & MONITORING ======
    # Stats détaillées de la company
    path('stats/', views.business_stats, name='business_stats'),
    
    # Résumé features actives  
    path('features-summary/', views.features_summary, name='features_summary'),
    
    # ====== LEGACY SUPPORT (COMPATIBILITÉ) ======
    # Endpoint de compatibilité pour trigger manuel
    path('trigger-creation/', views.trigger_business_creation, name='trigger_business_creation'),
]

# ====== DOCUMENTATION DES ENDPOINTS ======
"""
API Endpoints disponibles:

🆕 SETUP BUSINESS EXPLICITE (Option A)
---------------------------------------------
POST   /onboarding/business/setup/              → Créer business (remplace signal auto)
GET    /onboarding/business/setup-status/       → Status onboarding complet   
GET    /onboarding/business/check-eligibility/  → Vérifier éligibilité avant setup

📊 STATS & MONITORING
---------------------------------------------
GET    /onboarding/business/stats/              → Stats détaillées company
GET    /onboarding/business/features-summary/   → Features actives

🔧 LEGACY SUPPORT
---------------------------------------------
POST   /onboarding/business/trigger-creation/   → Trigger manuel (compatibilité)

📝 USAGE EXAMPLES:

1. Setup business explicite (recommandé):
   POST /onboarding/business/setup/
   {
     "business_name": "Mon Super Business"  // optionnel
   }

2. Vérifier éligibilité avant setup:
   GET /onboarding/business/check-eligibility/

3. Status complet après setup:
   GET /onboarding/business/setup-status/

4. Stats détaillées:
   GET /onboarding/business/stats/
"""