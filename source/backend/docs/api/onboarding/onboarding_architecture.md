# Architecture Onboarding - Documentation Complète

## Vue d'ensemble

Le système d'onboarding est composé de **4 apps spécialisées** qui gèrent le cycle de vie complet d'un utilisateur, de l'inscription à la gestion avancée des trials et upgrades.

```
🚀 onboarding_registration  → Inscription utilisateurs
🏢 onboarding_business      → Création business explicite  
📧 onboarding_invitations   → Invitations utilisateurs
📊 onboarding_trials        → Gestion trials & upgrades
```

---

## 🚀 onboarding_registration

### **Responsabilité**
Gestion de l'inscription utilisateur avec **architecture explicite** (plus de signal automatique).

### **Composants**

#### **Apps Configuration**
```python
# apps.py
class OnboardingRegistrationConfig(AppConfig):
    def ready(self):
        # Signal désactivé - Architecture explicite
        pass
```

#### **Services**
```python
# services/validation.py
- validate_user_eligibility()    # Éligibilité business
- can_trigger_business_creation() # Trigger manuel business
```

#### **URLs**
```bash
POST /onboarding/trigger-business-creation/  # Legacy endpoint
```

### **Flow d'inscription**
```
User créé via /users/ → User simple (pas de business)
                    ↓
                Appel explicite à /onboarding/business/setup/
                    ↓  
                Business créé avec OnboardingService
```

---

## 🏢 onboarding_business

### **Responsabilité**
**Cœur du système** - Création et gestion des business (Company + Brand + Features + Slots).

### **Architecture**

#### **Services Core**
```python
# services/onboarding.py
class OnboardingService:
    - is_user_eligible_for_business()  # Validation éligibilité
    - setup_business_for_user()        # Setup complet business
    - get_user_business_status()       # Status utilisateur

# services/business_creation.py  
- create_solo_business_for_user()      # Company + Brand + Trial
- get_business_creation_summary()      # Résumé création

# services/features_setup.py
- setup_default_features()            # Features par défaut
- get_company_features_summary()       # Résumé features

# services/slots_setup.py
- setup_default_slots()               # Quotas users/brands
- get_slots_usage_summary()           # Usage slots

# services/trial_setup.py  
- setup_trial_subscription()          # Subscription trial
- extend_trial_period()               # Extension trial

# services/roles_setup.py
- assign_default_roles()              # Rôles par défaut
- get_user_roles_summary()            # Résumé rôles
```

#### **API Endpoints**
```bash
# Setup Business Explicite  
POST /onboarding/business/setup/              # Créer business
GET  /onboarding/business/setup-status/       # Status complet
GET  /onboarding/business/check-eligibility/  # Vérifier éligibilité

# Stats & Monitoring
GET  /onboarding/business/stats/              # Stats détaillées 
GET  /onboarding/business/features-summary/   # Features actives

# Legacy Support
POST /onboarding/business/trigger-creation/   # Compatibilité
```

#### **Serializers**
```python
- BusinessSetupSerializer           # Input setup business
- BusinessStatusSerializer          # Status onboarding  
- BusinessStatsSerializer           # Stats détaillées
- BusinessEligibilitySerializer     # Éligibilité check
- BusinessSetupResponseSerializer   # Réponse création
```

#### **Permissions**
```python
- CanSetupBusiness     # User sans company
- CanExtendTrial       # Company admin only
- CanViewBusinessStats # Membres company
```

### **Flow Business Creation**
```
POST /onboarding/business/setup/ 
        ↓
OnboardingService.setup_business_for_user()
        ↓
1. create_solo_business_for_user()    # Company + Brand + user_type='agency_admin'
2. setup_default_slots()             # 2 users, 1 brand
3. setup_default_features()          # websites, templates, analytics  
4. setup_trial_subscription()        # Trial 2 semaines
5. assign_default_roles()            # company_admin, brand_admin, websites_admin
        ↓
Business Solo opérationnel (trial 2 sem)
```

---

## 📧 onboarding_invitations

### **Responsabilité**
Système d'invitations utilisateurs dans companies existantes.

### **Architecture**

#### **Models**
```python
# models/invitation.py
class UserInvitation:
    - company           # Company qui invite
    - invited_brand     # Brand spécifique
    - invited_by        # User inviteur
    - email            # Email invité
    - user_type        # brand_member | brand_admin
    - token            # UUID unique
    - status           # pending | accepted | expired | cancelled
    - expires_at       # Expiration (7 jours)
```

#### **Services**
```python
# services/invitation.py
- send_invitation()                # Envoyer invitation
- accept_invitation()              # Accepter via token
- get_invitation_status()          # Status invitation
- resend_invitation()              # Renvoyer invitation
- get_company_invitations()        # Liste invitations company

# services/validation.py  
- validate_invitation_permissions() # Permissions inviteur
- validate_invitation_slots()       # Slots disponibles
- validate_invitation_data()        # Données invitation
- validate_invitation_acceptance()  # Acceptation valide

# services/roles_assignment.py
- assign_invitation_roles()        # Rôles invited user
```

#### **URLs**
```bash
POST /onboarding/invitations/send/           # Envoyer invitation
POST /onboarding/invitations/accept/         # Accepter invitation  
GET  /onboarding/invitations/status/{token}/ # Status invitation
POST /onboarding/invitations/resend/{id}/    # Renvoyer invitation
GET  /onboarding/invitations/list/           # Liste invitations
```

### **Flow Invitation**
```
Company admin envoie invitation
        ↓
UserInvitation créée + Email envoyé
        ↓
User clique lien → Frontend appelle accept
        ↓
User assigné à Company + Brand + Rôles
        ↓
User devient member de la company existante
```

---

## 📊 onboarding_trials

### **Responsabilité**
Gestion avancée des trials, tracking événements, upgrades automatiques.

### **Architecture**

#### **Models**
```python
# models/trial_event.py
class TrialEvent:
    - company           # Company concernée
    - event_type        # trial_start | warning_7 | expired | auto_upgrade
    - event_data        # JSON événement
    - triggered_by      # User déclencheur
    - processed         # Événement traité
```

#### **Services**
```python
# services/trial.py
- create_trial_event()         # Créer événement
- start_trial_tracking()       # Démarrer tracking
- check_trial_warnings()       # Avertissements (7,3,1 jours)
- check_expired_trials()       # Trials expirés
- extend_trial()              # Étendre trial

# services/auto_upgrade.py
- check_auto_upgrade_trigger() # Solo → Agency (2+ brands)
- handle_agency_upgrade()      # Upgrade slots + billing
- trigger_manual_upgrade()     # Upgrade manuel

# services/billing_integration.py  
- handle_agency_upgrade_billing() # Billing auto-upgrade
- handle_manual_upgrade_billing() # Billing upgrade manuel
```

#### **URLs**
```bash
GET  /onboarding/trials/status/            # Status trial complet
POST /onboarding/trials/extend/            # Étendre trial
GET  /onboarding/trials/events/            # Événements trial
POST /onboarding/trials/upgrade/           # Upgrade manuel
GET  /onboarding/trials/upgrade-detection/ # Auto-upgrade detection
```

### **Flow Trial Management**
```
Business créé → trial_start event
        ↓
Tasks périodiques → check_trial_warnings() → notifications
        ↓
Add 2ème brand → check_auto_upgrade_trigger() → Agency upgrade
        ↓
Trial expire → check_expired_trials() → restrictions
```

---

## 🔄 Flow Global d'Onboarding

### **1. Inscription Normale**
```bash
POST /users/                           # User simple créé
POST /onboarding/business/setup/       # Business explicite
                ↓
Solo Business (1 brand, 2 slots users, trial 2 sem)
```

### **2. Invitation Utilisateur**  
```bash
POST /onboarding/invitations/send/     # Company admin invite
GET  /accept-invitation/{token}/       # User accepte
                ↓  
User rejoint company existante (brand_member)
```

### **3. Évolution Solo → Agency**
```bash
POST /brands/                          # Add 2ème brand
                ↓
Auto-upgrade déclenché → Slots 1→5 users → Billing upgrade
```

### **4. Gestion Trial**
```bash
Trial warnings (7,3,1 jours) → Notifications
Trial expire → Restrictions features
Manual upgrade → Plan payant
```

---

## 📋 Apps Dependencies

### **Core Dependencies**
```python
company_core    # Models Company  
brands_core     # Models Brand
users_core      # Models CustomUser
users_roles     # Système permissions granulaires
```

### **Business Dependencies**
```python
company_slots      # Quotas users/brands
company_features   # Features company
billing_core       # Plans & subscriptions  
billing_stripe     # Intégration Stripe
```

### **Architecture Relationship**
```
users_core ←→ onboarding_registration (validation users)
company_core ←→ onboarding_business (business creation)
brands_core ←→ onboarding_invitations (brand assignments)
billing_core ←→ onboarding_trials (upgrades & billing)
```

---

## 🎯 Points Clés Architecture

### **✅ Architecture Explicite**
- **Pas de signal automatique** - Flow contrôlé
- **Séparation responsabilités** claire entre apps
- **API REST pure** - Endpoints explicites

### **✅ Business Logic Robuste**
- **Solo vs Agency** auto-détection
- **Trial management** complet avec tracking
- **Permissions granulaires** avec users_roles
- **Slots management** avec quotas dynamiques

### **✅ Sécurité & Validation**
- **Validation éligibilité** à chaque étape
- **Permissions business** appropriées  
- **Gestion erreurs** granulaire
- **Contraintes DB** respectées

### **✅ Évolutivité**
- **Services modulaires** réutilisables
- **Events tracking** pour analytics
- **Integration billing** extensible
- **Multi-tenant** ready avec company scoping