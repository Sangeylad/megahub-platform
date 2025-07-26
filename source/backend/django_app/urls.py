# backend/django_app/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ========== AI INFRASTRUCTURE ========== 
    # 🧠 Intelligence artificielle centralisée
    path('ai/', include([
        # Hub central des jobs IA
        # GET/POST /ai/jobs/ → CRUD jobs IA
        # GET /ai/jobs/dashboard/ → Dashboard IA
        # GET /ai/job-types/ → Types de jobs disponibles
        path('', include(('ai_core.urls', 'ai_core'), namespace='ai_core')),
        
        # Providers et credentials
        # GET /ai/providers/ → Providers disponibles
        # GET/POST /ai/credentials/ → Credentials sécurisées
        # GET /ai/credentials/quota_status/ → Statut quotas
        path('', include(('ai_providers.urls', 'ai_providers'), namespace='ai_providers')),
        
        # OpenAI spécifique
        # GET /ai/openai/jobs/ → Jobs OpenAI
        # POST /ai/openai/chat/ → Chat completions
        path('openai/', include(('ai_openai.urls', 'ai_openai'), namespace='ai_openai')),
        
        # Usage et métriques
        # GET /ai/usage/ → Usage tracking
        # GET /ai/usage/dashboard/ → Dashboard usage
        # GET /ai/alerts/ → Alertes usage
        path('', include(('ai_usage.urls', 'ai_usage'), namespace='ai_usage')),
    ])),
    
    # ========== AUTHENTICATION SYSTEM ==========
    # 🔐 Authentication centralisée JWT
    path('auth/', include(('auth_core.urls', 'auth_core'), namespace='auth')),
    
    # ========== ONBOARDING SYSTEM ==========
    # 🚀 Système complet d'onboarding et gestion trials
    path('onboarding/', include([
        # Création business automatique
        # GET /onboarding/business/setup-status/ → Status création business
        # GET /onboarding/business/stats/ → Stats complètes business
        # GET /onboarding/business/features-summary/ → Résumé features actives
        path('business/', include(('onboarding_business.urls', 'onboarding_business'), namespace='onboarding_business')),
        
        # Gestion invitations utilisateurs
        # POST /onboarding/invitations/send/ → Envoyer invitation
        # POST /onboarding/invitations/accept/ → Accepter invitation
        # GET /onboarding/invitations/status/{token}/ → Status invitation
        # POST /onboarding/invitations/resend/{id}/ → Renvoyer invitation
        # GET /onboarding/invitations/list/ → Liste invitations company
        # POST /onboarding/invitations/validate-slots/ → Valider slots disponibles
        path('invitations/', include(('onboarding_invitations.urls', 'onboarding_invitations'), namespace='onboarding_invitations')),
        
        # Gestion trials et upgrades
        # GET /onboarding/trials/status/ → Status trial complet
        # POST /onboarding/trials/extend/ → Étendre période trial
        # GET /onboarding/trials/events/ → Événements trial
        # POST /onboarding/trials/upgrade/ → Demande upgrade manuel
        # GET /onboarding/trials/upgrade-detection/ → Détection auto-upgrade
        path('trials/', include(('onboarding_trials.urls', 'onboarding_trials'), namespace='onboarding_trials')),
        
        # Registration triggers (en dernier - fallback)
        # POST /onboarding/trigger-business-creation/ → Trigger manuel business
        path('', include(('onboarding_registration.urls', 'onboarding_registration'), namespace='onboarding_registration')),
    ])),
    
    # ========== WEBSITE MANAGEMENT - HUB PRINCIPAL ==========
    # 🎯 Toute la gestion website sous un seul préfixe logique
    path('websites/', include([
    # 🔧 FIX: Pages AVANT websites (ordre important !)
        path('pages/', include(('seo_pages_content.urls', 'seo_pages_content'), namespace='pages')),
        path('builder/', include(('seo_pages_layout.urls', 'seo_pages_layout'), namespace='builder')),
        path('structure/', include(('seo_pages_hierarchy.urls', 'seo_pages_hierarchy'), namespace='structure')),
        path('workflow/', include(('seo_pages_workflow.urls', 'seo_pages_workflow'), namespace='workflow')),
        path('seo/', include(('seo_pages_seo.urls', 'seo_pages_seo'), namespace='seo')),
        path('keywords/', include(('seo_pages_keywords.urls', 'seo_pages_keywords'), namespace='keywords')),
        path('categorization/', include(('seo_websites_categorization.urls', 'seo_websites_categorization'), namespace='categorization')),

        # 🔧 Sites web en DERNIER (catch-all)
        path('', include(('seo_websites_core.urls', 'seo_websites_core'), namespace='sites')),
    ])),
    
        # ========== DESIGN SYSTEM ==========
        # 🎨 Système de design centralisé (colors, typography, spacing, tailwind)
        path('design/', include([
            # Gestion des couleurs
            # GET/POST /design/colors/brand-palettes/ → CRUD palettes marque
            # GET/POST /design/colors/website-configs/ → Config couleurs sites
            # GET /design/colors/website-configs/{id}/css-variables/ → Export CSS variables
            path('colors/', include(('brands_design_colors.urls', 'brands_design_colors'), namespace='design_colors')),
            
            # Système typographique
            # GET/POST /design/typography/brand-typography/ → CRUD typography marque
            # GET/POST /design/typography/website-configs/ → Config typography sites
            # GET /design/typography/website-configs/{id}/font-sizes/ → Export échelles
            path('typography/', include(('brands_design_typography.urls', 'brands_design_typography'), namespace='design_typography')),
            
            # Espacement et layout
            # GET/POST /design/spacing/brand-spacing/ → CRUD spacing marque
            # GET/POST /design/spacing/website-configs/ → Config layout sites
            # GET /design/spacing/brand-spacing/{id}/tailwind-spacing/ → Export Tailwind spacing
            path('spacing/', include(('brands_design_spacing.urls', 'brands_design_spacing'), namespace='design_spacing')),
            
            # Configuration Tailwind
            # GET/POST /design/tailwind/website-configs/ → Config Tailwind sites
            # POST /design/tailwind/website-configs/{id}/regenerate-config/ → Régénération
            # GET /design/tailwind/website-configs/{id}/export-config/ → Export (JS/CSS/JSON)
            path('tailwind/', include(('brands_design_tailwind.urls', 'brands_design_tailwind'), namespace='design_tailwind')),
        ])),
        
     # ========== TEMPLATES IA ==========
        # 🎯 Système de templates pour génération de contenu IA
        path('templates/', include([
            # Templates spécialisés SEO
            # GET /templates/seo/seo-templates/ → Templates SEO spécialisés
            path('seo/', include(('seo_websites_ai_templates_content.urls', 'seo_websites_ai_templates_content'), namespace='template_seo')),
            
            # Workflow et validation
            # GET /templates/workflow/approvals/ → Processus approbation
            path('workflow/', include(('ai_templates_workflow.urls', 'ai_templates_workflow'), namespace='template_workflow')),
            
            # Analytics et métriques
            # GET /templates/analytics/usage-metrics/ → Métriques usage
            path('analytics/', include(('ai_templates_analytics.urls', 'ai_templates_analytics'), namespace='template_analytics')),
            
            # Intelligence et recommandations
            # GET /templates/insights/recommendations/ → Recommandations IA
            path('insights/', include(('ai_templates_insights.urls', 'ai_templates_insights'), namespace='template_insights')),
            
            # Variables et versioning
            # GET /templates/storage/variables/ → Variables disponibles
            path('storage/', include(('ai_templates_storage.urls', 'ai_templates_storage'), namespace='template_storage')),
            
            # Organisation et catégories (préfixées pour éviter conflit)
            # GET /templates/categories/ → CRUD catégories hiérarchiques
            # GET /templates/tags/ → CRUD tags libres
            path('categories/', include(('ai_templates_categories.urls', 'ai_templates_categories'), namespace='template_categories')),
            
            # Core templates en DERNIER (catch-all pour racine)
            # GET/POST /templates/ → CRUD templates
            # GET /templates/types/ → Types de templates
            # POST /templates/{id}/duplicate/ → Dupliquer
            path('', include(('ai_templates_core.urls', 'ai_templates_core'), namespace='templates')),
        ])),
        
        # ========== MAILING SYSTEM ==========
      # 📧 Système complet de mailing et email marketing
      path('mailing/', include([
          # Gestion des abonnés et contacts
          # GET/POST /mailing/contacts/ → CRUD abonnés email
          # GET /mailing/contacts/stats/ → Statistiques abonnés
          # POST /mailing/contacts/{id}/subscribe/ → Réabonner
          # POST /mailing/contacts/{id}/unsubscribe/ → Désabonner
          # POST /mailing/contacts/bulk-import/ → Import en masse
          path('contacts/', include([
              # Préférences et consentements RGPD
              # GET/PUT /mailing/contacts/preferences/ → CRUD préférences
              # POST /mailing/contacts/preferences/gdpr-consent/ → Gestion RGPD
              path('preferences/', include(('mailing_contacts_preferences.urls', 'mailing_contacts_preferences'), namespace='contacts_preferences')),
              
              # Tracking comportemental et engagement
              # GET /mailing/contacts/tracking/ → Métriques engagement
              # GET /mailing/contacts/tracking/stats/ → Stats comportementales
              path('tracking/', include(('mailing_contacts_tracking.urls', 'mailing_contacts_tracking'), namespace='contacts_tracking')),
              
              # Lifecycle marketing automation
              # GET/PUT /mailing/contacts/lifecycle/ → Étapes lifecycle
              # GET /mailing/contacts/lifecycle/funnel/ → Analyse funnel
              path('lifecycle/', include(('mailing_contacts_lifecycle.urls', 'mailing_contacts_lifecycle'), namespace='contacts_lifecycle')),
              
              # 🔧 Contacts core en DERNIER (catch-all)
              # GET/POST /mailing/contacts/ → CRUD abonnés email principal
              path('', include(('mailing_contacts_core.urls', 'mailing_contacts_core'), namespace='contacts')),
          ])),
          
          # Gestion des listes et segmentation
          # GET/POST /mailing/lists/ → CRUD listes de diffusion
          # GET /mailing/lists/{id}/subscribers/ → Abonnés d'une liste
          # POST /mailing/lists/{id}/add-subscribers/ → Ajouter abonnés
          # POST /mailing/lists/{id}/remove-subscribers/ → Retirer abonnés
          # GET /mailing/lists/stats/ → Statistiques listes
          path('lists/', include([
              # Segmentation avancée avec critères
              # GET/POST /mailing/lists/segments/ → CRUD segments dynamiques
              # POST /mailing/lists/segments/{id}/evaluate/ → Réévaluer segment
              path('segments/', include(('mailing_lists_segments.urls', 'mailing_lists_segments'), namespace='lists_segments')),
              
              # Import/export de listes
              # POST /mailing/lists/imports/ → Import CSV/Excel
              # GET /mailing/lists/imports/{id}/status/ → Status import
              # GET /mailing/lists/exports/ → Export listes
              path('imports/', include(('mailing_lists_imports.urls', 'mailing_lists_imports'), namespace='lists_imports')),
              
              # Compliance et suppression lists
              # GET/POST /mailing/lists/suppressions/ → CRUD suppressions
              # POST /mailing/lists/compliance/check/ → Vérification conformité
              path('compliance/', include(('mailing_lists_compliance.urls', 'mailing_lists_compliance'), namespace='lists_compliance')),
              
              # 🔧 Listes core en DERNIER (catch-all)
              # GET/POST /mailing/lists/ → CRUD listes principales
              path('', include(('mailing_lists_core.urls', 'mailing_lists_core'), namespace='lists')),
          ])),
          
          # Gestion des templates email
          # GET/POST /mailing/templates/ → CRUD templates email
          # POST /mailing/templates/{id}/duplicate/ → Dupliquer template
          # POST /mailing/templates/{id}/toggle-favorite/ → Favoris
          # GET /mailing/templates/{id}/preview/ → Prévisualisation
          path('templates/', include([
              # Versioning et historique des templates
              # GET/POST /mailing/templates/versions/ → CRUD versions
              # POST /mailing/templates/{id}/create-version/ → Nouvelle version
              # POST /mailing/templates/versions/{id}/rollback/ → Rollback version
              path('versions/', include(('mailing_templates_versions.urls', 'mailing_templates_versions'), namespace='templates_versions')),
              
              # 🔧 Templates core en DERNIER (catch-all)
              # GET/POST /mailing/templates/ → CRUD templates principaux
              path('', include(('mailing_templates_core.urls', 'mailing_templates_core'), namespace='templates')),
          ])),
          
          # Campagnes et envois
          # GET/POST /mailing/campaigns/ → CRUD campagnes email
          # POST /mailing/campaigns/{id}/send/ → Envoyer maintenant
          # POST /mailing/campaigns/{id}/schedule/ → Programmer envoi
          # POST /mailing/campaigns/{id}/pause/ → Mettre en pause
          # POST /mailing/campaigns/{id}/duplicate/ → Dupliquer campagne
          path('campaigns/', include([
              # Gestion des envois et delivery
              # GET /mailing/campaigns/sending/ → Status envois en cours
              # GET /mailing/campaigns/sending/{id}/progress/ → Progression envoi
              # POST /mailing/campaigns/sending/{id}/pause/ → Pause envoi
              path('sending/', include(('mailing_campaigns_sending.urls', 'mailing_campaigns_sending'), namespace='campaigns_sending')),
              
              # 🔧 Campagnes core en DERNIER (catch-all)
              # GET/POST /mailing/campaigns/ → CRUD campagnes principales
              path('', include(('mailing_campaigns_core.urls', 'mailing_campaigns_core'), namespace='campaigns')),
          ])),
          
          # Analytics et événements
          # GET /mailing/analytics/events/ → Événements email
          # GET /mailing/analytics/events/dashboard/ → Dashboard analytics
          # GET /mailing/analytics/events/trends/ → Tendances temporelles
          path('analytics/', include([
              # Tracking ouvertures détaillé
              # GET /mailing/analytics/opens/ → Analytics ouvertures
              # GET /mailing/analytics/opens/heatmap/ → Heatmap ouvertures
              path('opens/', include(('mailing_analytics_opens.urls', 'mailing_analytics_opens'), namespace='analytics_opens')),
              
              # Tracking clics avec attribution
              # GET /mailing/analytics/clicks/ → Analytics clics
              # GET /mailing/analytics/clicks/links/ → Performance liens
              path('clicks/', include(('mailing_analytics_clicks.urls', 'mailing_analytics_clicks'), namespace='analytics_clicks')),
              
              # Tracking conversions et ROI
              # GET /mailing/analytics/conversions/ → Analytics conversions
              # GET /mailing/analytics/conversions/roi/ → Calculs ROI
              path('conversions/', include(('mailing_analytics_conversions.urls', 'mailing_analytics_conversions'), namespace='analytics_conversions')),
              
              # Rapports et dashboards custom
              # GET/POST /mailing/analytics/reports/ → CRUD rapports
              # GET /mailing/analytics/reports/{id}/generate/ → Générer rapport
              path('reports/', include(('mailing_analytics_reports.urls', 'mailing_analytics_reports'), namespace='analytics_reports')),
              
              # 🔧 Analytics core en DERNIER (catch-all)
              # GET /mailing/analytics/events/ → Événements centralisés
              path('', include(('mailing_analytics_core.urls', 'mailing_analytics_core'), namespace='analytics')),
          ])),
          
          # Automations et workflows
          # GET/POST /mailing/automations/ → CRUD automations
          # POST /mailing/automations/{id}/activate/ → Activer automation
          # POST /mailing/automations/{id}/pause/ → Pause automation
          path('automations/', include([
              # Déclencheurs des automations
              # GET/POST /mailing/automations/triggers/ → CRUD triggers
              # POST /mailing/automations/triggers/{id}/test/ → Test trigger
              path('triggers/', include(('mailing_automations_triggers.urls', 'mailing_automations_triggers'), namespace='automations_triggers')),
              
              # Actions des automations
              # GET/POST /mailing/automations/actions/ → CRUD actions
              # GET /mailing/automations/actions/types/ → Types d'actions
              path('actions/', include(('mailing_automations_actions.urls', 'mailing_automations_actions'), namespace='automations_actions')),
              
              # Conditions et logique métier
              # GET/POST /mailing/automations/conditions/ → CRUD conditions
              # POST /mailing/automations/conditions/evaluate/ → Test conditions
              path('conditions/', include(('mailing_automations_conditions.urls', 'mailing_automations_conditions'), namespace='automations_conditions')),
              
              # Séquences drip campaigns
              # GET/POST /mailing/automations/sequences/ → CRUD séquences
              # GET /mailing/automations/sequences/{id}/performance/ → Performance séquence
              path('sequences/', include(('mailing_automations_sequences.urls', 'mailing_automations_sequences'), namespace='automations_sequences')),
              
              # 🔧 Automations core en DERNIER (catch-all)
              # GET/POST /mailing/automations/ → CRUD automations principales
              path('', include(('mailing_automations_core.urls', 'mailing_automations_core'), namespace='automations')),
          ])),
          
          # Deliverability et conformité
          # GET /mailing/deliverability/ → Status deliverability global
          # GET /mailing/deliverability/reputation/ → Score réputation
          path('deliverability/', include([
              # Email warming (lemwarm-like)
              # GET/POST /mailing/deliverability/warming/ → CRUD campagnes warming
              # GET /mailing/deliverability/warming/{id}/metrics/ → Métriques warming
              # POST /mailing/deliverability/warming/{id}/adjust/ → Ajuster algorithme
              path('warming/', include(('mailing_deliverability_warming.urls', 'mailing_deliverability_warming'), namespace='deliverability_warming')),
              
              # Monitoring deliverability temps réel
              # GET /mailing/deliverability/monitoring/ → Dashboard monitoring
              # GET /mailing/deliverability/monitoring/inbox-rate/ → Taux inbox
              path('monitoring/', include(('mailing_deliverability_monitoring.urls', 'mailing_deliverability_monitoring'), namespace='deliverability_monitoring')),
              
              # Gestion des bounces
              # GET /mailing/deliverability/bounces/ → Analytics bounces
              # POST /mailing/deliverability/bounces/suppress/ → Suppression automatique
              path('bounces/', include(('mailing_deliverability_bounces.urls', 'mailing_deliverability_bounces'), namespace='deliverability_bounces')),
              
              # Configuration SPF/DKIM/DMARC
              # GET/PUT /mailing/deliverability/authentication/ → Config DNS
              # POST /mailing/deliverability/authentication/verify/ → Vérification DNS
              path('authentication/', include(('mailing_deliverability_authentication.urls', 'mailing_deliverability_authentication'), namespace='deliverability_authentication')),
              
              # Suivi réputation domaine/IP
              # GET /mailing/deliverability/reputation/ → Historique réputation
              # GET /mailing/deliverability/reputation/alerts/ → Alertes réputation
              path('reputation/', include(('mailing_deliverability_reputation.urls', 'mailing_deliverability_reputation'), namespace='deliverability_reputation')),
              
              # 🔧 Deliverability core en DERNIER (catch-all)
              # GET /mailing/deliverability/ → Configuration globale
              path('', include(('mailing_deliverability_core.urls', 'mailing_deliverability_core'), namespace='deliverability')),
          ])),
          
          # Intégrations externes
          # GET /mailing/integrations/ → Liste intégrations actives
          # POST /mailing/integrations/{id}/sync/ → Synchronisation manuelle
          path('integrations/', include([
              # Sync bidirectionnelle avec CRM
              # GET/POST /mailing/integrations/crm/ → CRUD sync CRM
              # POST /mailing/integrations/crm/sync-contacts/ → Sync contacts
              path('crm/', include(('mailing_integrations_crm.urls', 'mailing_integrations_crm'), namespace='integrations_crm')),
              
              # Connexions API externes
              # GET/POST /mailing/integrations/api/ → CRUD connexions API
              # POST /mailing/integrations/api/{id}/test/ → Test connexion
              path('api/', include(('mailing_integrations_api.urls', 'mailing_integrations_api'), namespace='integrations_api')),
              
              # Intégration formulaires web
              # GET/POST /mailing/integrations/forms/ → CRUD formulaires
              # GET /mailing/integrations/forms/{id}/embed/ → Code embed
              path('forms/', include(('mailing_integrations_forms.urls', 'mailing_integrations_forms'), namespace='integrations_forms')),
              
              # 🔧 Intégrations core en DERNIER (catch-all)
              # GET /mailing/integrations/ → Hub intégrations
              path('', include(('mailing_integrations_core.urls', 'mailing_integrations_core'), namespace='integrations')),
          ])),
          
          # Configuration et paramètres
          # GET /mailing/config/ → Configuration globale mailing
          path('config/', include([
              # Configuration domaines d'envoi
              # GET/POST /mailing/config/domains/ → CRUD domaines
              # POST /mailing/config/domains/{id}/verify/ → Vérification DNS
              path('domains/', include(('mailing_configuration_domains.urls', 'mailing_configuration_domains'), namespace='config_domains')),
              
              # Permissions utilisateurs mailing
              # GET/PUT /mailing/config/users/ → Permissions granulaires
              # GET /mailing/config/users/roles/ → Rôles disponibles
              path('users/', include(('mailing_configuration_users.urls', 'mailing_configuration_users'), namespace='config_users')),
              
              # Configuration branding emails
              # GET/PUT /mailing/config/branding/ → Templates marque
              # GET /mailing/config/branding/preview/ → Prévisualisation
              path('branding/', include(('mailing_configuration_branding.urls', 'mailing_configuration_branding'), namespace='config_branding')),
              
              # Quotas et rate limiting
              # GET/PUT /mailing/config/limits/ → Limites envoi
              # GET /mailing/config/limits/usage/ → Usage actuel
              path('limits/', include(('mailing_configuration_limits.urls', 'mailing_configuration_limits'), namespace='config_limits')),
              
              # 🔧 Configuration core en DERNIER (catch-all)
              # GET/PUT /mailing/config/ → Paramètres globaux
              path('', include(('mailing_configuration_core.urls', 'mailing_configuration_core'), namespace='config')),
          ])),
      ])),
        
        # ========== BUSINESS CORE EXTENDED ==========
        # 🏢 Gestion des entreprises et facturation
        path('companies/', include([
            # Gestion des slots et features
            # GET/POST /companies/slots/ → CRUD slots d'entreprise
            # GET/POST /companies/features/ → CRUD features d'entreprise
            path('slots/', include(('company_slots.urls', 'company_slots'), namespace='company_slots')),

            path('features/', include(('company_features.urls', 'company_features'), namespace='company_features')),

            
            # Companies core en DERNIER (catch-all pour racine)
            # GET/POST /companies/ → CRUD entreprises
            # GET /companies/{id}/billing-summary/ → Résumé facturation
            # POST /companies/{id}/check-limits/ → Vérifier limites
            path('', include(('company_core.urls', 'company_core'), namespace='companies')),
        ])),
        
        # ========== BRANDS EXTENDED ==========
        # 🎯 Gestion des marques
        path('brands/', include([
            # ✅ CORRECTION : Une seule registration brands_core
            # GET/POST /brands/ → CRUD marques
            # POST /brands/{id}/assign-users/ → Assigner utilisateurs
            # POST /brands/{id}/set-admin/ → Définir admin
            path('', include(('brands_core.urls', 'brands_core'), namespace='brands')),
        ])),
        
        # ========== USERS EXTENDED ==========
        # 👥 Gestion des utilisateurs et rôles
        path('users/', include([
            # 🎯 Roles avec préfixes AVANT (spécifique)
            path('', include(('users_roles.urls', 'users_roles'), namespace='users_roles')),
            
            # 🔧 Users core APRÈS (catch-all pour /users/ directement)
            path('', include(('users_core.urls', 'users_core'), namespace='users')),
        ])),
        
        # ========== BILLING SYSTEM ==========
        # 💳 Système de facturation complet
        path('billing/', include([
            # Intégration Stripe
            # GET/POST /billing/stripe/customers/ → Clients Stripe
            # GET/POST /billing/stripe/payment-methods/ → Méthodes de paiement
            # POST /billing/stripe/checkout/create-session/ → Sessions checkout
            # POST /billing/stripe/webhooks/ → Webhooks Stripe
            path('stripe/', include(('billing_stripe.urls', 'billing_stripe'), namespace='billing_stripe')),


            
            # Billing core en DERNIER (catch-all pour racine)
            # GET/POST /billing/plans/ → CRUD plans
            # GET/POST /billing/subscriptions/ → CRUD abonnements
            # GET/POST /billing/invoices/ → CRUD factures
            # GET/POST /billing/alerts/ → CRUD alertes d'utilisation
            path('', include(('billing_core.urls', 'billing_core'), namespace='billing')),
        ])),
    
    
    # ========== BLOG MANAGEMENT ==========
    # 📝 Gestion complète du système de blog
    path('blogs/', include([
        # Configuration blog par website
        # GET/PUT /blogs/config/ → Configuration blog (1 par website)
        # GET /blogs/config/templates/ → Templates disponibles
        path('config/', include(('blog_config.urls', 'blog_config'), namespace='blog_config')),
        
        # Workflow de publication
        # GET/PUT /blogs/status/ → Gestion statuts
        # GET /blogs/status/dashboard/ → Dashboard éditorial
        # POST /blogs/scheduled/ → Publications programmées
        path('publishing/', include(('blog_publishing.urls', 'blog_publishing'), namespace='blog_publishing')),
        
        path('collections/', include(('blog_collections.urls', 'blog_collections'), namespace='blog_collections')),

        
        # Éditeur avancé
        # GET/PUT /blogs/content/ → Contenu TipTap
        # POST /blogs/content/{id}/autosave/ → Sauvegarde auto
        path('editor/', include(('blog_editor.urls', 'blog_editor'), namespace='blog_editor')),
        
        # Gestion contenu de base (en dernier pour catch-all)
        # GET/POST /blogs/articles/ → CRUD articles
        # GET/POST /blogs/authors/ → CRUD auteurs  
        # GET/POST /blogs/tags/ → CRUD tags
        path('', include(('blog_content.urls', 'blog_content'), namespace='blog_content')),
    ])),
    
    path('tasks/', include('task_core.urls')),
    path('tasks/scheduled/', include('task_scheduling.urls')),
    path('tasks/monitoring/', include('task_monitoring.urls')),
    path('tasks/persistent-jobs/', include('task_persistence.urls')),
    
    # ========== SEO RESEARCH & ANALYSIS ==========
    # 🔍 Recherche mots-clés et cocons (logique séparée du website management)
    path('seo/', include([
        # Base de données mots-clés globale
        # GET/POST /seo/keywords/ → CRUD mots-clés avec tous filtres
        # GET /seo/keywords/?cocoon=5 → Mots-clés d'un cocon
        # GET /seo/keywords/?da_median__gte=50 → Filtres métriques avancés
        path('keywords/', include(('seo_keywords_base.urls', 'seo_keywords_base'), namespace='seo_keywords')),
        
        # Gestion cocons sémantiques
        # GET/POST /seo/cocoons/ → CRUD cocons eux-mêmes
        # GET/POST /seo/cocoons/categories/ → Catégories de cocons
        # GET /seo/cocoons/{id}/stats/ → Statistiques cocon
        path('cocoons/', include(('seo_keywords_cocoons.urls', 'seo_keywords_cocoons'), namespace='seo_cocoons')),
    ])),
    

    
    # ========== TOOLS & UTILITIES ==========
    # 🛠️ Outils utilitaires regroupés logiquement
    path('tools/', include([
        # Conversion de fichiers
        # POST /tools/files/pdf-to-text/ → Conversion PDF vers texte
        # POST /tools/files/docx-to-html/ → Conversion DOCX vers HTML
        path('files/', include('file_converter.urls')),
        
        # Compression
        # POST /tools/compress/images/ → Compression images (WebP, JPEG)
        # POST /tools/compress/videos/ → Compression vidéos
        path('compress/', include('file_compressor.urls')),
        
        # Outils publics
        # GET/POST /tools/public/qr-generator/ → Générateur QR codes
        # GET/POST /tools/public/password-generator/ → Générateur mots de passe
        path('public/', include('public_tools.urls')),
        
        # Raccourcisseur d'URLs
        # POST /tools/short/create/ → Créer URL courte
        # GET /tools/short/{code}/ → Redirection
    #    path('short/', include('url_shortener.urls')),
    ])),
    
    # ========== GLOSSARY ==========
    # 📚 Glossaire marketing/SEO
    # GET /glossaire/terms/ → Termes du glossaire
    # GET /glossaire/categories/ → Catégories de termes
    path('glossaire/', include('glossary.urls')),
]