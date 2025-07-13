# Onboarding System API Documentation

## Vue d'ensemble

Le système `onboarding` gère la création des business et les invitations utilisateurs. Il se compose de quatre apps :

1. **`onboarding_business`** : Création et setup complet des business
2. **`onboarding_invitations`** : Système d'invitations utilisateurs dans les brands  
3. **`onboarding_registration`** : Trigger manuel de création business (fallback)
4. **`onboarding_trials`** : Gestion avancée des trials et upgrades

---

# Onboarding Business API

## Vue d'ensemble

L'app `onboarding_business` gère la création et le setup complet des business pour les utilisateurs. Elle remplace l'ancien système de signaux automatiques par un setup explicite et contrôlé.

### Architecture

- **Namespace**: `onboarding_business`
- **Base URL**: `/onboarding/business/`
- **Approche**: RESTful API avec setup explicite
- **Transaction Safety**: Toutes les opérations de création utilisent `transaction.atomic()`

---

## Endpoints API

### 🆕 Setup Business Explicite

#### POST `/onboarding/business/setup/`
**Créer un business complet pour l'utilisateur connecté**

- **Permissions**: `IsAuthenticated`, `CanSetupBusiness`
- **Méthode**: `POST`
- **View**: `BusinessSetupView.post()`

**Request Body:**
```

---

# Onboarding Invitations API

## Vue d'ensemble

L'app `onboarding_invitations` gère le système d'invitations pour recruter des utilisateurs dans les brands. Elle permet d'inviter, accepter et gérer les invitations avec validation des slots et permissions.

### Architecture

- **Namespace**: `onboarding_invitations`
- **Base URL**: `/onboarding/invitations/`
- **Approche**: RESTful API avec validation métier
- **Expiration**: 7 jours par défaut
- **Transaction Safety**: Acceptation d'invitation en transaction atomique

---

## Endpoints API

### 📤 Envoi d'Invitations

#### POST `/onboarding/invitations/send/`
**Envoyer une invitation utilisateur**

- **Permissions**: `IsAuthenticated`, `IsBrandAdmin`
- **Méthode**: `POST`
- **View**: `send_user_invitation()`

**Request Body:**
```json
{
  "email": "user@example.com",
  "brand_id": 1,
  "user_type": "brand_member",
  "invitation_message": "string"  // optionnel, max 1000 chars
}
```

**User Types Disponibles:**
- `"brand_member"`: Membre Marque (défaut)
- `"brand_admin"`: Admin Marque

**Response Success (201):**
```json
{
  "success": true,
  "message": "Invitation envoyée avec succès",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "status": "pending",
    "user_type": "brand_member",
    "company_name": "Ma Company",
    "brand_name": "Ma Brand",
    "invited_by_name": "John Doe",
    "expires_at": "2025-07-18T12:00:00Z",
    "is_valid": true,
    "is_expired": false,
    "invitation_message": "Bienvenue !"
  }
}
```

**Response Error (400):**
```json
{
  "error": "Données invalides",
  "details": {
    "email": ["Cette adresse email est déjà invitée"],
    "brand_id": ["Brand non trouvée"]
  }
}
```

**Response Error (404):**
```json
{
  "error": "Brand non trouvée"
}
```

---

#### POST `/onboarding/invitations/accept/`
**Accepter une invitation**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `POST`
- **View**: `accept_user_invitation()`

**Request Body:**
```json
{
  "token": "uuid-token-here"
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "Invitation acceptée avec succès",
  "data": {
    "company_id": 1,
    "company_name": "Ma Company",
    "brand_id": 1,
    "brand_name": "Ma Brand",
    "user_type": "brand_member"
  }
}
```

**Response Error (400):**
```json
{
  "error": "Erreur acceptation invitation",
  "details": "Invitation expirée ou déjà utilisée"
}
```

---

### 📋 Gestion des Invitations

#### GET `/onboarding/invitations/status/<uuid:token>/`
**Status d'une invitation (endpoint public)**

- **Permissions**: Aucune (endpoint public)
- **Méthode**: `GET`
- **View**: `invitation_status()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "found": true,
    "invitation": {
      "id": 1,
      "email": "user@example.com",
      "status": "pending",
      "user_type": "brand_member",
      "company_name": "Ma Company",
      "brand_name": "Ma Brand",
      "invited_by": "John Doe",
      "expires_at": "2025-07-18T12:00:00Z",
      "is_valid": true,
      "invitation_url": "/accept-invitation/uuid-token/"
    }
  }
}
```

**Response Not Found:**
```json
{
  "success": true,
  "data": {
    "found": false,
    "error": "Invitation non trouvée"
  }
}
```

---

#### POST `/onboarding/invitations/resend/<int:invitation_id>/`
**Renvoyer une invitation**

- **Permissions**: `IsAuthenticated`, `IsBrandAdmin`
- **Méthode**: `POST`
- **View**: `resend_user_invitation()`

**Response Success (200):**
```json
{
  "success": true,
  "message": "Invitation renvoyée avec succès",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "status": "pending",
    "expires_at": "2025-07-18T12:00:00Z",
    "is_valid": true
  }
}
```

---

#### GET `/onboarding/invitations/list/`
**Liste des invitations de la company**

- **Permissions**: `IsAuthenticated`, `IsBrandMember`
- **Méthode**: `GET`
- **View**: `list_company_invitations()`

**Query Parameters:**
- `status`: Filtrer par statut (`pending`, `accepted`, `expired`, `cancelled`)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "invitations": [
      {
        "id": 1,
        "email": "user@example.com",
        "status": "pending",
        "user_type": "brand_member",
        "company_name": "Ma Company",
        "brand_name": "Ma Brand",
        "invited_by_name": "John Doe",
        "accepted_by_name": null,
        "expires_at": "2025-07-18T12:00:00Z",
        "accepted_at": null,
        "created_at": "2025-07-11T12:00:00Z",
        "is_valid": true,
        "is_expired": false,
        "invitation_message": "Bienvenue !"
      }
    ],
    "total": 1
  }
}
```

---

#### POST `/onboarding/invitations/validate-slots/`
**Valider slots disponibles pour invitations**

- **Permissions**: `IsAuthenticated`, `IsBrandAdmin`
- **Méthode**: `POST`
- **View**: `validate_invitation_slots()`

**Request Body:**
```json
{
  "emails": ["user1@example.com", "user2@example.com"]
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "Slots disponibles pour invitations",
  "data": {
    "emails_count": 2,
    "company_slots": 3
  }
}
```

**Response Error (400):**
```json
{
  "error": "Validation slots échouée",
  "details": "Pas assez de slots disponibles. Besoin: 3, Disponibles: 1"
}
```

---

## Model UserInvitation

### Champs

**Relations:**
- `company`: `ForeignKey` - Company qui invite
- `invited_brand`: `ForeignKey` - Brand spécifique d'invitation  
- `invited_by`: `ForeignKey` - User qui a envoyé l'invitation
- `accepted_by`: `ForeignKey` - User qui a accepté (nullable)

**User Invité:**
- `email`: `EmailField` - Email de l'utilisateur invité
- `user_type`: `CharField` - Type utilisateur à assigner

**Invitation Details:**
- `token`: `UUIDField` - Token unique d'invitation
- `status`: `CharField` - Status de l'invitation
- `invitation_message`: `TextField` - Message personnalisé

**Dates:**
- `expires_at`: `DateTimeField` - Date d'expiration (7 jours par défaut)
- `accepted_at`: `DateTimeField` - Date d'acceptation (nullable)

### Statuts d'Invitation

- `"pending"`: En attente (défaut)
- `"accepted"`: Acceptée
- `"expired"`: Expirée
- `"cancelled"`: Annulée

### User Types

- `"brand_member"`: Membre Marque (défaut)
- `"brand_admin"`: Admin Marque

### Méthodes du Model

**`is_valid()`**
- Vérifie si invitation encore valide
- Returns: `bool` (status='pending' et non expirée)

**`is_expired()`**
- Vérifie si invitation expirée
- Returns: `bool`

**`mark_as_expired()`**
- Marque comme expirée
- Update: `status='expired'`

**`accept(user)`**
- Accepte l'invitation et configure l'user
- Actions: Assigne user à company/brand, assigne rôles
- Raises: `ValueError` si invalide

**`cancel()`**
- Annule l'invitation
- Update: `status='cancelled'`

**`resend()`**
- Renouvelle l'invitation
- Actions: Reset expiration, renvoie email

**`get_invitation_url()`**
- URL d'acceptation
- Returns: `/accept-invitation/{token}/`

**`get_summary()`**
- Résumé pour API
- Returns: `dict` avec infos principales

### Contraintes Model

**Indexes:**
- `token` (unique)
- `email, status`
- `company, status`
- `expires_at`

**Unique Together:**
- `company, email, status` (une seule invitation pending par email/company)

---

## Serializers

### InvitationCreateSerializer
**Création d'invitation**

**Champs:**
- `email`: `EmailField` (requis)
- `brand_id`: `IntegerField` (requis)
- `user_type`: `ChoiceField` (`brand_member`, `brand_admin`, défaut: `brand_member`)
- `invitation_message`: `CharField` (optionnel, max 1000 chars)

**Validation:**
- Email valide et non déjà membre de la company
- Brand existe et appartient à la company
- User_type valide

### InvitationSerializer
**UserInvitation complet**

**Champs (read-only):**
- `id`: `IntegerField`
- `email`: `CharField`
- `status`: `CharField`
- `user_type`: `CharField`
- `company_name`: `CharField` (from company.name)
- `brand_name`: `CharField` (from invited_brand.name)
- `invited_by_name`: `SerializerMethodField`
- `accepted_by_name`: `SerializerMethodField`
- `expires_at`: `DateTimeField`
- `accepted_at`: `DateTimeField`
- `created_at`: `DateTimeField`
- `is_valid`: `SerializerMethodField`
- `is_expired`: `SerializerMethodField`
- `invitation_message`: `TextField`

### InvitationAcceptSerializer
**Acceptation d'invitation**

**Champs:**
- `token`: `UUIDField` (requis)

**Validation:**
- Token existe et correspond à une invitation

### InvitationStatusSerializer
**Status d'invitation**

**Champs:**
- `found`: `BooleanField`
- `invitation`: `DictField` (si trouvée)
- `error`: `CharField` (si non trouvée)

---

## Services

### InvitationService

**`send_invitation(invited_by, company, brand, email, user_type, message)`**
- Envoie une invitation utilisateur
- Validation: permissions, slots, données
- Actions: Crée invitation, envoie email
- Returns: `UserInvitation`
- Raises: `ValidationError`

**`accept_invitation(token, user)`**
- Accepte une invitation via token
- Validation: token valide, user éligible
- Actions: Assigne user, marque acceptée, assigne rôles
- Returns: `UserInvitation`
- Raises: `ValidationError`

**`get_invitation_status(token)`**
- Status d'une invitation via token
- Returns: `dict` avec found/invitation/error

**`resend_invitation(invitation_id, user)`**
- Renvoie une invitation
- Validation: permissions
- Actions: Reset expiration, renvoie email
- Returns: `UserInvitation`

**`get_company_invitations(company, status=None)`**
- Liste des invitations d'une company
- Filtre: par status optionnel
- Returns: `QuerySet`

**`cleanup_expired_invitations()`**
- Nettoie les invitations expirées (task périodique)
- Actions: Mark expired les invitations past expires_at
- Returns: `int` (count nettoyées)

### ValidationService

**`validate_invitation_permissions(user, company, brand)`**
- Valide permissions pour envoyer invitation
- Vérifications: can_invite_users, company access, brand access
- Raises: `PermissionDenied`

**`validate_invitation_slots(company, invited_emails)`**
- Valide slots disponibles pour invitations
- Calculs: pending invitations + nouvelles vs slots disponibles
- Raises: `ValidationError`

**`validate_invitation_data(email, user_type, company, brand)`**
- Valide données d'invitation
- Vérifications: email format, user pas déjà membre, user_type valide
- Raises: `ValidationError`

**`validate_invitation_acceptance(invitation, user)`**
- Valide acceptation d'invitation
- Vérifications: invitation valide, emails match, user pas assigné
- Raises: `ValidationError`

### EmailService

**`send_invitation_email(invitation)`**
- Envoie email d'invitation
- Template: subject + message avec lien d'acceptation
- Returns: `bool`

**`send_invitation_reminder(invitation)`**
- Envoie rappel invitation
- Uses: même template que send_invitation_email
- Returns: `bool`

**`get_invitation_email_template(invitation)`**
- Template email d'invitation
- Returns: `dict` avec subject, recipient, template, context

### RolesAssignmentService

**`assign_invitation_roles(user, invitation)`**
- Assigne rôles pour user qui accepte invitation
- Rôles brand_member: `brand_member`, `websites_editor`
- Rôles brand_admin: `brand_admin`, `websites_admin`
- Returns: `list[UserRole]`

**`get_invitation_available_roles()`**
- Rôles disponibles pour invitations
- Returns: `dict` par user_type

---

## Business Logic

### Flow d'Invitation Complet

#### 1. Validation Préalable
```
POST /onboarding/invitations/validate-slots/
→ Vérifie slots disponibles pour liste emails
```

#### 2. Envoi Invitation
```
POST /onboarding/invitations/send/
→ Valide permissions + slots + données
→ Crée UserInvitation + envoie email
→ Status: pending, expires dans 7 jours
```

#### 3. Consultation Status (Public)
```
GET /onboarding/invitations/status/{token}/
→ Vérifie validité invitation via token
→ Endpoint public (pas d'auth)
```

#### 4. Acceptation Invitation
```
POST /onboarding/invitations/accept/
→ Valide token + user éligible
→ Assigne user à company/brand + rôles
→ Status: accepted
```

#### 5. Gestion (Admin)
```
GET /onboarding/invitations/list/
→ Liste invitations company avec filtres

POST /onboarding/invitations/resend/{id}/
→ Renouvelle invitation expirée
```

### Validations Métier

**Permissions Requises:**
- **Envoyer**: `IsBrandAdmin` + `can_invite_users()` + accès brand
- **Accepter**: `IsAuthenticated` + email match + pas déjà assigné
- **Lister**: `IsBrandMember` de la company
- **Renvoyer**: `IsBrandAdmin` + accès invitation

**Slots Validation:**
- Compte invitations pending + nouvelles invitations
- Compare avec `company.slots.get_available_users_slots()`
- Bloque si dépassement

**Expiration Gestion:**
- Défaut: 7 jours après création
- Auto-expire: via task périodique `cleanup_expired_invitations`
- Renouveau: `resend()` reset l'expiration

### User Types et Rôles

**brand_member → Rôles:**
- `brand_member`: Accès de base à la brand
- `websites_editor`: Edition websites

**brand_admin → Rôles:**
- `brand_admin`: Administration complète brand
- `websites_admin`: Administration websites

### Email Integration

**Template Variables:**
- `invitation`: Object UserInvitation
- `invited_by`: User qui invite
- `company`: Company d'invitation
- `brand`: Brand cible
- `acceptance_url`: Lien d'acceptation
- `expires_at`: Date expiration

**Email Flow:**
1. Création invitation → Envoi immédiat
2. Resend → Nouvel envoi avec nouvelle expiration
3. Reminder → Même template (à implémenter)

---

## Codes d'Erreur

| Code | Statut | Description |
|------|--------|-------------|
| 400 | Bad Request | Données invalides, slots insuffisants, invitation invalide |
| 401 | Unauthorized | Non authentifié |
| 403 | Forbidden | Permissions insuffisantes |
| 404 | Not Found | Brand/Invitation non trouvée |
| 500 | Internal Error | Erreur technique |

---

## Configuration Requise

### Dépendances
- `company_core.models.Company`
- `brands_core.models.Brand`
- `users_core.models.CustomUser`
- `company_slots.models.CompanySlots`
- `users_roles.models.Role, UserRole` (optionnel)
- `common.permissions.business_permissions.IsBrandAdmin, IsBrandMember`

### Settings
```python
# Frontend URL pour liens d'invitation
FRONTEND_URL = 'https://app.megahub.com'

# Email configuration pour envoi invitations
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

---

## Exemples d'Usage

### Flow Complet d'Invitation

```bash
# 1. Valider slots disponibles
curl -X POST /onboarding/invitations/validate-slots/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user@example.com"]}'

# 2. Envoyer invitation
curl -X POST /onboarding/invitations/send/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "brand_id": 1,
    "user_type": "brand_member",
    "invitation_message": "Bienvenue dans notre équipe !"
  }'

# 3. Vérifier status (endpoint public)
curl -X GET /onboarding/invitations/status/<uuid-token>/

# 4. Accepter invitation (côté invité)
curl -X POST /onboarding/invitations/accept/ \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{"token": "<uuid-token>"}'

# 5. Lister invitations company
curl -X GET /onboarding/invitations/list/?status=pending \
  -H "Authorization: Bearer <token>"

# 6. Renvoyer invitation expirée
curl -X POST /onboarding/invitations/resend/1/ \
  -H "Authorization: Bearer <token>"
```

### Gestion des Erreurs

**Slots Insuffisants:**
```json
{
  "error": "Validation slots échouée",
  "details": "Pas assez de slots disponibles. Besoin: 3 (nouvelles: 2, pending: 1), Disponibles: 1"
}
```

**Invitation Expirée:**
```json
{
  "error": "Erreur acceptation invitation", 
  "details": "Invitation expirée ou déjà utilisée"
}
```

**Permissions Insuffisantes:**
```json
{
  "error": "Erreur envoi invitation",
  "details": "Permissions insuffisantes pour inviter"
}
```

---

# Onboarding Registration API

## Vue d'ensemble

L'app `onboarding_registration` fournit des utilitaires de fallback pour la création de business. Elle permet de déclencher manuellement la création d'un business quand le système automatique échoue ou n'est pas disponible.

### Architecture

- **Namespace**: `onboarding_registration`
- **Base URL**: `/onboarding/registration/`
- **Approche**: Endpoints de fallback et trigger manuel
- **Usage**: Complément à `onboarding_business` pour cas d'exception

---

## Endpoints API

### 🔧 Trigger Manuel

#### POST `/onboarding/registration/trigger-business-creation/`
**Déclencher manuellement la création business**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `POST`
- **View**: `trigger_business_creation()`
- **Usage**: Fallback si signal automatique a échoué

**Request Body:**
```json
{
  "business_name": "string"  // optionnel
}
```

**Response Success (201):**
```json
{
  "success": true,
  "message": "Business créé avec succès",
  "data": {
    "company_id": 1,
    "brand_id": 1,
    "is_trial": true
  }
}
```

**Response Error (400):**
```json
{
  "error": "User non éligible pour création business",
  "details": "User déjà assigné à une company ou contraintes non respectées"
}
```

**Response Error (500):**
```json
{
  "error": "Erreur lors de la création business",
  "details": "Message d'erreur technique détaillé"
}
```

---

## Services

### ValidationService

**`validate_user_eligibility(user)`**
- Valide qu'un user peut créer un business automatiquement
- Vérifications: company=None, is_active=True, not superuser, not staff
- Returns: `bool`

**Conditions d'Éligibilité:**
- ✅ `user.company is None` (pas déjà assigné)
- ✅ `user.is_active = True` (compte actif)
- ❌ `user.is_superuser = False` (pas admin platform)
- ❌ `user.is_staff = False` (pas staff platform)

**`can_trigger_business_creation(user)`**
- Vérifie si user peut déclencher manuellement la création business
- Uses: `validate_user_eligibility()` + logique anti-spam (TODO)
- Returns: `bool`

---

## Business Logic

### Cas d'Usage

**Trigger Manuel Nécessaire:**
1. Signal automatique échoué lors de registration
2. User créé par admin sans business
3. Restauration après problème technique
4. Migration de données

### Validation d'Éligibilité

**Users Éligibles:**
- Nouveaux users sans company assignée
- Comptes actifs non-administrateurs
- Users sans contraintes spéciales

**Users Non-Éligibles:**
- Users déjà assignés à une company
- Comptes inactifs (`is_active=False`)
- Super-utilisateurs (`is_superuser=True`)
- Staff platform (`is_staff=True`)

### Intégration avec onboarding_business

**Délégation:**
- Utilise `onboarding_business.services.business_creation.create_solo_business_for_user()`
- Même logique que le setup automatique
- Transaction atomique garantie

**Différences:**
- Trigger manuel vs automatique
- Endpoint dédié pour debugging/support
- Logging spécifique pour traçabilité

---

## Codes d'Erreur

| Code | Statut | Description |
|------|--------|-------------|
| 400 | Bad Request | User non éligible (déjà assigné, inactif, etc.) |
| 401 | Unauthorized | Non authentifié |
| 500 | Internal Error | Erreur technique lors création business |

---

## Configuration Requise

### Dépendances
- `onboarding_business.services.business_creation.create_solo_business_for_user`
- `users_core.models.CustomUser`

### Pas de Models
Cette app ne définit pas de models propres, elle utilise les services d'autres apps.

---

## Exemples d'Usage

### Trigger Manuel de Business

```bash
# Créer business pour user éligible
curl -X POST /onboarding/registration/trigger-business-creation/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"business_name": "Mon Business Manuel"}'

# Trigger sans nom spécifique (généré automatiquement)
curl -X POST /onboarding/registration/trigger-business-creation/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Gestion des Erreurs

**User Déjà Assigné:**
```json
{
  "error": "User non éligible pour création business",
  "details": "User déjà assigné à une company ou contraintes non respectées"
}
```

**Erreur Technique:**
```json
{
  "error": "Erreur lors de la création business",
  "details": "Company.DoesNotExist: Company matching query does not exist"
}
```

---

## Logging et Monitoring

**Events Loggés:**
- `INFO`: Business créé manuellement avec user.username
- `DEBUG`: User éligibilité (détails refus)
- `ERROR`: Erreurs techniques avec stack trace

**Format de Log:**
```
INFO - Business créé manuellement pour john.doe
DEBUG - User jane.smith déjà assigné à company Acme Corp
ERROR - Erreur création business manuelle pour bob.wilson: [détails]
```

---

## Comparaison des Apps Onboarding

| Feature | onboarding_business | onboarding_invitations | onboarding_registration | onboarding_trials |
|---------|--------------------|-----------------------|------------------------|--------------------|
| **Scope** | Setup business complet | Invitations users | Trigger manuel fallback | Analytics & auto-upgrade |
| **Endpoints** | 6 (CRUD + stats) | 6 (send + accept + manage) | 1 (trigger only) | 5 (status + extend + upgrade) |
| **Models** | Aucun (utilise services) | UserInvitation | Aucun | TrialEvent |
| **Services** | 6 services complets | 4 services spécialisés | 1 service validation | 3 services (trial/upgrade/billing) |
| **Permissions** | Business-level | Brand-level | User-level | Company-level |
| **Usage** | Setup initial | Recrutement équipe | Fallback/debugging | Monitoring & upgrades |
| **Transaction** | Atomique complète | Atomique (acceptance) | Atomique (délégation) | Event-driven |
| **Tasks Celery** | 3 (maintenance) | 1 (cleanup) | Aucune | 3 (daily/weekly/monthly) |
| **Auto-Logic** | Signal-based setup | Email workflow | Manuel uniquement | Auto-upgrade & warnings |

---

## Architecture Globale du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEGAHUB ONBOARDING SYSTEM                   │
├─────────────────────┬─────────────────────┬─────────────────────┤
│  onboarding_business │ onboarding_invitations │ onboarding_registration │
│                     │                     │                     │
│ • Setup complet     │ • Inviter users     │ • Trigger manuel    │
│ • Trial & Features  │ • Accepter invites  │ • Validation simple │
│ • Slots & Rôles     │ • Gestion tokens    │ • Fallback system   │
│ • Stats détaillées  │ • Email workflow    │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

**Flow Recommandé:**
1. **Registration** → User créé
2. **Business** → Setup automatique complet via `onboarding_business`
3. **Invitations** → Recruter équipe via `onboarding_invitations`
4. **Registration** → Fallback manuel si problème via `onboarding_registration`

---

# Onboarding Trials API

## Vue d'ensemble

L'app `onboarding_trials` gère la logique avancée des trials, l'auto-upgrade des companies et le tracking des événements. Elle fournit des analytics détaillées et automatise les transitions entre les modes business.

### Architecture

- **Namespace**: `onboarding_trials`
- **Base URL**: `/onboarding/trials/`
- **Approche**: Event-driven avec analytics et auto-upgrade
- **Auto-upgrade**: Solo → Agency automatique (2e brand créée)
- **Tasks**: Monitoring quotidien + analytics hebdomadaires

---

## Endpoints API

### 📊 Status et Analytics

#### GET `/onboarding/trials/status/`
**Status complet du trial avec analytics**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `GET`
- **View**: `trial_status()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "is_trial": true,
    "trial_expires_at": "2025-07-25T12:00:00Z",
    "days_remaining": 14,
    "events_count": 3,
    "events": [
      {
        "id": 1,
        "event_type": "trial_start",
        "event_type_display": "Trial démarré",
        "event_data": {
          "trial_expires_at": "2025-07-25T12:00:00Z",
          "trial_duration_weeks": 2
        },
        "triggered_by": "john.doe",
        "processed": true,
        "created_at": "2025-07-11T12:00:00Z"
      }
    ],
    "last_event": {
      "event_type": "trial_start",
      "created_at": "2025-07-11T12:00:00Z"
    }
  }
}
```

---

#### GET `/onboarding/trials/events/`
**Liste des événements trial**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `GET`
- **View**: `trial_events()`

**Query Parameters:**
- `event_type`: Filtrer par type d'événement
- `limit`: Limite résultats (défaut: 20)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": 1,
        "event_type": "trial_start",
        "event_type_display": "Trial démarré",
        "event_data": {"trial_duration_weeks": 2},
        "triggered_by": "john.doe",
        "processed": true,
        "created_at": "2025-07-11T12:00:00Z"
      },
      {
        "id": 2,
        "event_type": "auto_upgrade",
        "event_type_display": "Upgrade automatique",
        "event_data": {
          "from_mode": "solo",
          "to_mode": "agency",
          "brands_count": 2,
          "trigger": "second_brand_created"
        },
        "triggered_by": "john.doe",
        "processed": true,
        "created_at": "2025-07-15T10:30:00Z"
      }
    ],
    "total": 2
  }
}
```

---

### ⚡ Gestion des Trials

#### POST `/onboarding/trials/extend/`
**Étendre la période de trial**

- **Permissions**: `IsAuthenticated`, `IsCompanyAdmin`
- **Méthode**: `POST`
- **View**: `extend_trial_period()`

**Request Body:**
```json
{
  "additional_weeks": 1
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "Trial étendu de 1 semaine(s)",
  "data": {
    "new_expires_at": "2025-08-01T12:00:00Z",
    "days_remaining": 21
  }
}
```

**Response Error (400):**
```json
{
  "error": "Extension trial impossible",
  "details": "Company pas en trial ou déjà expirée"
}
```

---

### 🚀 Upgrades

#### POST `/onboarding/trials/upgrade/`
**Demander upgrade manuel**

- **Permissions**: `IsAuthenticated`, `IsCompanyAdmin`
- **Méthode**: `POST`
- **View**: `request_upgrade()`

**Request Body:**
```json
{
  "plan_type": "professional"
}
```

**Plan Types Disponibles:**
- `"starter"`: Plan de base
- `"professional"`: Plan professionnel
- `"enterprise"`: Plan entreprise

**Response Success (200):**
```json
{
  "success": true,
  "message": "Upgrade vers professional initié",
  "data": {
    "plan_type": "professional",
    "company_mode": "agency"
  }
}
```

**Response Error (500):**
```json
{
  "error": "Upgrade échoué",
  "details": "Erreur lors du processus upgrade"
}
```

---

#### GET `/onboarding/trials/upgrade-detection/`
**Détection auto-upgrade et opportunities**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `GET`
- **View**: `upgrade_detection()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "business_mode": "agency",
    "is_solo": false,
    "is_agency": true,
    "brands_count": 2,
    "auto_upgraded": true,
    "upgrade_opportunities": {
      "current_plan": {
        "name": "Plan Starter",
        "price": 0
      },
      "available_plans": [
        {
          "plan_type": "professional",
          "name": "Plan Professional",
          "price": 29.99,
          "features": ["5 users", "Unlimited brands", "Advanced analytics"]
        },
        {
          "plan_type": "enterprise",
          "name": "Plan Enterprise", 
          "price": 99.99,
          "features": ["Unlimited users", "Custom integrations", "Priority support"]
        }
      ]
    }
  }
}
```

---

## Model TrialEvent

### Champs

**Relations:**
- `company`: `ForeignKey` - Company concernée

**Event Details:**
- `event_type`: `CharField` - Type d'événement trial
- `event_data`: `JSONField` - Données JSON de l'événement
- `triggered_by`: `ForeignKey` - User qui a déclenché (nullable)
- `processed`: `BooleanField` - Événement traité

### Types d'Événements

- `"trial_start"`: Trial démarré
- `"trial_warning_7"`: Avertissement 7 jours
- `"trial_warning_3"`: Avertissement 3 jours
- `"trial_warning_1"`: Avertissement 1 jour
- `"trial_expired"`: Trial expiré
- `"trial_extended"`: Trial étendu
- `"auto_upgrade"`: Upgrade automatique
- `"manual_upgrade"`: Upgrade manuel
- `"trial_converted"`: Trial converti

### Méthodes du Model

**`mark_as_processed()`**
- Marque l'événement comme traité
- Update: `processed=True`

**`get_event_summary()`**
- Résumé pour API
- Returns: `dict` avec infos complètes

---

## Services

### TrialService

**`create_trial_event(company, event_type, event_data=None, triggered_by=None)`**
- Crée un événement trial
- Returns: `TrialEvent`

**`start_trial_tracking(company)`**
- Démarre le tracking trial pour une company
- Actions: Crée event `trial_start`

**`check_trial_warnings()`**
- Vérifie et envoie les avertissements trial (task quotidienne)
- Seuils: 7j, 3j, 1j avant expiration
- Returns: `int` (nombre warnings envoyés)

**`check_expired_trials()`**
- Vérifie les trials expirés (task quotidienne)
- Actions: Crée events `trial_expired`, gère expiration
- Returns: `int` (nombre trials expirés)

**`extend_trial(company, additional_weeks=1, triggered_by=None)`**
- Étend un trial
- Actions: Update company, étend subscription/features, crée event
- Returns: `bool`

**`get_trial_analytics(company)`**
- Analytics trial pour une company
- Returns: `dict` avec status, events, analytics

**`send_trial_warning_notification(company, days_remaining)`**
- Envoie notification trial warning (TODO: intégrer notifications)

**`handle_trial_expiration(company)`**
- Gère l'expiration d'un trial (TODO: logique métier)

### AutoUpgradeService

**`check_auto_upgrade_trigger(company, triggered_by=None)`**
- Vérifie et déclenche upgrade automatique solo → agency
- Trigger: Création 2e brand
- Actions: Crée event `auto_upgrade`, upgrade slots/billing
- Returns: `bool`

**`handle_agency_upgrade(company)`**
- Gère l'upgrade vers mode agency
- Actions: Upgrade slots users (1→5), upgrade billing
- Integration: `upgrade_slots_for_agency()`, `handle_agency_upgrade_billing()`

**`trigger_manual_upgrade(company, plan_type, triggered_by)`**
- Déclenche upgrade manuel
- Actions: Crée event `manual_upgrade`, upgrade billing
- Returns: `bool`

**`get_upgrade_opportunities()`**
- Identifie les companies candidates pour upgrade
- Analytics: solo_in_trial, auto_upgrade_candidates
- Returns: `dict` avec compteurs

### BillingIntegrationService

**`handle_agency_upgrade_billing(company)`**
- Gère l'aspect billing de l'upgrade agency
- Actions: Upgrade vers plan professional, update subscription
- Integration: `billing_core.models.Plan, Subscription`

**`handle_manual_upgrade_billing(company, plan_type)`**
- Gère billing pour upgrade manuel
- Actions: Crée ou upgrade subscription vers plan choisi
- Returns: None

**`get_billing_upgrade_summary(company)`**
- Résumé billing upgrade pour company
- Returns: `dict` avec current_plan, available_plans

---

## Tasks Celery

### @shared_task daily_trial_check
**Vérifications quotidiennes des trials**

- **Cron**: Quotidien (suggéré: 8h)
- **Actions**: `check_trial_warnings()` + `check_expired_trials()`
- **Monitoring**: Warnings envoyés + trials expirés traités

### @shared_task weekly_upgrade_analysis
**Analyse hebdomadaire des opportunities**

- **Cron**: Hebdomadaire (suggéré: dimanche)
- **Actions**: `get_upgrade_opportunities()`
- **Analytics**: Compteurs d'opportunités upgrade

### @shared_task cleanup_old_trial_events
**Nettoyage mensuel des vieux events**

- **Cron**: Mensuel
- **Actions**: Supprime events > 90 jours et processed=True
- **Returns**: Compteur events supprimés

---

## Business Logic

### Auto-Upgrade Flow

**Trigger Automatique:**
1. Company crée 2e brand → `is_agency()` = True
2. Check auto-upgrade trigger → Pas déjà upgradée
3. Crée event `auto_upgrade` avec métadata
4. Upgrade slots: 1→5 users via `upgrade_slots_for_agency()`
5. Upgrade billing: starter→professional via billing integration

**Conditions Auto-Upgrade:**
- ✅ `company.is_agency()` = True (2+ brands)
- ❌ Pas d'event `auto_upgrade` existant
- ✅ Company active

### Trial Warnings System

**Timeline Automatique:**
- **J-7**: Event `trial_warning_7` + notification
- **J-3**: Event `trial_warning_3` + notification
- **J-1**: Event `trial_warning_1` + notification
- **J-0**: Event `trial_expired` + gestion expiration

**Anti-Doublon:**
- Check events existants avant création
- Un seul warning par seuil par company

### Manual Upgrade Process

**User-Initiated:**
1. Company admin request upgrade via endpoint
2. Validation plan_type disponible
3. Crée event `manual_upgrade` avec plan choisi
4. Billing integration: crée/upgrade subscription
5. Return success/failure

**Plans Disponibles:**
- `starter`: Plan gratuit/trial
- `professional`: Plan professionnel (29.99€)
- `enterprise`: Plan entreprise (99.99€)

### Event Data Schema

**trial_start:**
```json
{
  "trial_expires_at": "2025-07-25T12:00:00Z",
  "trial_duration_weeks": 2
}
```

**trial_warning_X:**
```json
{
  "days_remaining": 7,
  "trial_expires_at": "2025-07-25T12:00:00Z"
}
```

**auto_upgrade:**
```json
{
  "from_mode": "solo",
  "to_mode": "agency", 
  "brands_count": 2,
  "trigger": "second_brand_created"
}
```

**manual_upgrade:**
```json
{
  "plan_type": "professional",
  "previous_mode": "solo",
  "brands_count": 1
}
```

**trial_extended:**
```json
{
  "old_expires_at": "2025-07-25T12:00:00Z",
  "new_expires_at": "2025-08-01T12:00:00Z", 
  "additional_weeks": 1
}
```

---

## Codes d'Erreur

| Code | Statut | Description |
|------|--------|-------------|
| 400 | Bad Request | Company sans trial, données invalides, extension impossible |
| 401 | Unauthorized | Non authentifié |
| 403 | Forbidden | Pas company admin |
| 500 | Internal Error | Erreur technique upgrade/extension |

---

## Configuration Requise

### Dépendances
- `company_core.models.Company`
- `users_core.models.CustomUser`
- `billing_core.models.Plan, Subscription` (optionnel)
- `onboarding_business.services.slots_setup.upgrade_slots_for_agency`
- `onboarding_business.services.trial_setup.extend_trial_period`
- `common.permissions.business_permissions.IsCompanyAdmin`

### Settings Celery
```python
CELERY_BEAT_SCHEDULE = {
    'trials-daily-check': {
        'task': 'onboarding_trials.tasks.daily_trial_check',
        'schedule': crontab(hour=8, minute=0),  # 8h quotidien
    },
    'trials-weekly-analysis': {
        'task': 'onboarding_trials.tasks.weekly_upgrade_analysis',
        'schedule': crontab(hour=10, minute=0, day_of_week=0),  # Dimanche 10h
    },
    'trials-monthly-cleanup': {
        'task': 'onboarding_trials.tasks.cleanup_old_trial_events',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),  # 1er du mois 2h
    },
}
```

---

## Exemples d'Usage

### Monitoring Trial Complet

```bash
# 1. Status trial avec analytics
curl -X GET /onboarding/trials/status/ \
  -H "Authorization: Bearer <token>"

# 2. Historique événements
curl -X GET /onboarding/trials/events/?event_type=trial_warning_7&limit=10 \
  -H "Authorization: Bearer <token>"

# 3. Détection auto-upgrade
curl -X GET /onboarding/trials/upgrade-detection/ \
  -H "Authorization: Bearer <token>"
```

### Gestion Administrative

```bash
# 1. Étendre trial (company admin)
curl -X POST /onboarding/trials/extend/ \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"additional_weeks": 2}'

# 2. Request upgrade manuel
curl -X POST /onboarding/trials/upgrade/ \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"plan_type": "professional"}'
```

### Analytics et Monitoring

**Events Timeline:**
```json
[
  {"event_type": "trial_start", "created_at": "2025-07-11T12:00:00Z"},
  {"event_type": "auto_upgrade", "created_at": "2025-07-15T10:30:00Z"},
  {"event_type": "trial_warning_7", "created_at": "2025-07-18T08:00:00Z"},
  {"event_type": "trial_extended", "created_at": "2025-07-19T14:20:00Z"},
  {"event_type": "manual_upgrade", "created_at": "2025-07-22T16:45:00Z"}
]
```

**Upgrade Opportunities:**
```json
{
  "solo_in_trial": 15,
  "auto_upgrade_candidates": 8,
  "total_opportunities": 23
}
```

---

## Architecture Globale du Système

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           MEGAHUB ONBOARDING SYSTEM                                    │
├──────────────────┬─────────────────────┬─────────────────────┬─────────────────────────┤
│ onboarding_business │ onboarding_invitations │ onboarding_registration │   onboarding_trials   │
│                  │                     │                     │                         │
│ • Setup complet  │ • Inviter users     │ • Trigger manuel    │ • Analytics trials      │
│ • Trial & Features│ • Accepter invites  │ • Validation simple │ • Auto-upgrade logic    │
│ • Slots & Rôles  │ • Gestion tokens    │ • Fallback system   │ • Billing integration   │
│ • Stats détaillées│ • Email workflow    │                     │ • Events tracking       │
│                  │                     │                     │ • Monitoring tasks      │
└──────────────────┴─────────────────────┴─────────────────────┴─────────────────────────┘
```json
{
  "business_name": "string"  // optionnel, max 255 chars, min 2 chars
}
```

**Validation Rules:**
- `business_name`: Optionnel, généré automatiquement si non fourni
- Pattern autorisé: `^[a-zA-Z0-9\s\-&\.\'\"À-ÿ]+$`
- Pas que des espaces/caractères spéciaux

**Response Success (201):**
```json
{
  "success": true,
  "message": "Business créé avec succès",
  "data": {
    "company_id": 1,
    "company_name": "string",
    "brand_id": 1,
    "brand_name": "string",
    "is_trial": true,
    "trial_days_remaining": 14,
    "slots_info": {
      "users_slots": 2,
      "brands_slots": 1
    }
  }
}
```

**Response Error (400):**
```json
{
  "success": false,
  "error": "User non éligible pour création business",
  "details": "User déjà assigné à la company 'Nom Company'"
}
```

**Response Error (500):**
```json
{
  "success": false,
  "error": "Erreur lors de la création business",
  "details": "Message d'erreur détaillé"
}
```

---

#### GET `/onboarding/business/setup-status/`
**Status d'onboarding complet de l'utilisateur**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `GET`
- **View**: `BusinessSetupStatusView.get()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "string",
    "is_eligible_for_business": false,
    "has_business": true,
    "onboarding_complete": true,
    "business_summary": {
      "company_id": 1,
      "company_name": "string",
      "business_mode": "solo",
      "is_trial": true,
      "trial_days_remaining": 13,
      "brands_count": 1,
      "users_count": 1,
      "permissions": {...}
    }
  }
}
```

---

#### GET `/onboarding/business/check-eligibility/`
**Vérifier l'éligibilité avant setup**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `GET`
- **View**: `check_setup_eligibility()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "string",
    "is_eligible": true,
    "has_existing_business": false,
    "ineligibility_reason": null  // présent si is_eligible = false
  }
}
```

**Raisons d'inéligibilité possibles:**
- `"User déjà assigné à la company 'Nom Company'"`
- `"Les utilisateurs staff ne peuvent pas créer de business"`
- `"Les super-utilisateurs ne peuvent pas créer de business"`
- `"L'utilisateur n'est pas actif"`
- `"Raison inconnue"`

---

### 📊 Stats & Monitoring

#### GET `/onboarding/business/stats/`
**Statistiques détaillées de la company**

- **Permissions**: `IsAuthenticated`, `CanViewBusinessStats`
- **Méthode**: `GET`
- **View**: `business_stats()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "company_stats": {
      "business_mode": "solo",
      "is_in_trial": true,
      "trial_days_remaining": 13,
      "brands_stats": {...},
      "users_stats": {...}
    },
    "slots_usage": {
      "brands": {
        "current": 1,
        "limit": 1,
        "available": 0,
        "percentage": 100.0,
        "can_add": false
      },
      "users": {
        "current": 1,
        "limit": 2,
        "available": 1,
        "percentage": 50.0,
        "can_add": true
      }
    },
    "features_summary": {
      "total_features": 3,
      "active_features": [...]
    },
    "trial_summary": {
      "is_trial": true,
      "trial_expires_at": "2025-07-25T08:30:00Z",
      "days_remaining": 13,
      "can_extend": true
    }
  }
}
```

---

#### GET `/onboarding/business/features-summary/`
**Résumé des features actives**

- **Permissions**: `IsAuthenticated`, `CanViewBusinessStats`
- **Méthode**: `GET`
- **View**: `features_summary()`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_features": 3,
    "active_features": [
      {
        "name": "websites",
        "display_name": "Création Websites",
        "is_premium": false,
        "usage_limit": null,
        "current_usage": 0,
        "usage_percentage": 0.0,
        "expires_at": "2025-07-25T08:30:00Z",
        "is_active": true
      }
    ]
  }
}
```

---

### 🔧 Legacy Support

#### POST `/onboarding/business/trigger-creation/`
**Trigger manuel pour compatibilité**

- **Permissions**: `IsAuthenticated`
- **Méthode**: `POST`
- **View**: `trigger_business_creation()`

**Request Body:**
```json
{
  "business_name": "string"  // optionnel
}
```

**Response Success (201):**
```json
{
  "success": true,
  "message": "Business créé avec succès",
  "data": {
    "company_id": 1,
    "brand_id": 1,
    "is_trial": true
  }
}
```

---

## Serializers

### BusinessSetupSerializer
**Validation pour la création de business**

**Champs:**
- `business_name`: `CharField(required=False, max_length=255)`
  - Validators: `MinLengthValidator(2)`, `MaxLengthValidator(255)`
  - Pattern: `^[a-zA-Z0-9\s\-&\.\'\"À-ÿ]+$`

### BusinessStatusSerializer
**Status d'onboarding complet**

**Champs (read-only):**
- `user_id`: `IntegerField`
- `username`: `CharField`
- `is_eligible_for_business`: `BooleanField`
- `has_business`: `BooleanField`
- `onboarding_complete`: `BooleanField`
- `business_summary`: `DictField`

### BusinessStatsSerializer
**Stats détaillées du business**

**Champs (read-only):**
- `company_stats`: `DictField`
- `slots_usage`: `DictField`
- `features_summary`: `DictField`
- `trial_summary`: `DictField`
- `user_roles`: `DictField`
- `permissions_summary`: `DictField`

### BusinessEligibilitySerializer
**Vérification d'éligibilité**

**Champs (read-only):**
- `user_id`: `IntegerField`
- `username`: `CharField`
- `is_eligible`: `BooleanField`
- `has_existing_business`: `BooleanField`
- `ineligibility_reason`: `CharField(required=False)`
- `can_setup_business`: `BooleanField`

---

## Services

### OnboardingService
**Service principal d'onboarding**

#### Méthodes principales:

**`is_user_eligible_for_business(user)`**
- Vérifie l'éligibilité d'un user
- Returns: `bool`

**`setup_business_for_user(user, business_name=None)`**
- Setup complet d'un business
- Returns: `dict` avec `company`, `brand`, `slots`, `features`, etc.
- Raises: `UserNotEligibleError`, `BusinessAlreadyExistsError`

**`get_user_business_status(user)`**
- Status complet du business
- Returns: `dict` avec status détaillé

**`extend_trial_period(company, additional_weeks=1)`**
- Étend la période de trial
- Returns: `bool`

### Autres Services

**`create_solo_business_for_user(user, business_name=None)`**
- Crée Company + Brand + assignation user
- Returns: `{'company': Company, 'brand': Brand}`

**`setup_default_features(company)`**
- Active les features par défaut: `websites`, `templates`, `analytics`
- Returns: `list[CompanyFeature]`

**`setup_default_slots(company)`**
- Configure slots: `users_slots=2`, `brands_slots=1`
- Returns: `CompanySlots`

**`setup_trial_subscription(company)`**
- Crée subscription trial avec plan starter
- Returns: `Subscription or None`

**`assign_default_roles(user, company, brand)`**
- Assigne rôles: `company_admin`, `brand_admin`, `websites_admin`
- Returns: `list[UserRole]`

---

## Tasks Celery

### @shared_task daily_onboarding_maintenance
**Maintenance quotidienne système**

- **Cron**: `0 8 * * *` (8h tous les jours)
- **Intégration**: `task_core.models.Task`
- **Monitoring**: Trials expirant (7j, 3j, 1j, aujourd'hui)

### @shared_task cleanup_onboarding_data
**Nettoyage périodique**

- **Cron**: `0 2 * * 0` (Dimanche 2h)
- **Type**: `PersistentJob` (reprise possible)
- **Action**: Supprime companies deleted > 90 jours

### @shared_task trigger_business_analysis
**Analyse business sur demande**

- **Type**: Manuel
- **Input**: `company_id`
- **Output**: Analyse complète business

---

## Permissions

### CanSetupBusiness
**Setup business - User sans company**
```python
has_permission(request, view):
    return user.is_authenticated and user.company is None
```

### CanExtendTrial
**Extension trial - Company admin uniquement**
```python
has_permission(request, view):
    return user.is_authenticated and user.is_company_admin()
```

### CanViewBusinessStats
**Stats business - Membres company**
```python
has_permission(request, view):
    return user.is_authenticated and user.company is not None
```

---

## Exceptions

### OnboardingError
**Erreur de base onboarding**
- Base class pour toutes les erreurs onboarding

### UserNotEligibleError
**User non éligible**
- `__init__(user, reason)`
- Message: `"User {username} non éligible: {reason}"`

### BusinessAlreadyExistsError
**Business existe déjà**
- `__init__(user)`
- Message: `"User {username} a déjà un business"`

### SlotsLimitReachedError
**Limite slots atteinte**
- `__init__(company, slot_type)`
- Message: `"Limite {slot_type} atteinte pour {company.name}"`

### TrialExpiredError
**Trial expiré**
- `__init__(company)`
- Message: `"Trial expiré pour {company.name}"`

### OnboardingValidationError
**Validation API (extends ValidationError)**

### OnboardingPermissionError
**Permissions API (extends PermissionDenied)**

---

## Business Logic

### Business Modes
- `"solo"`: 1 user, 1 brand (défaut)
- `"agency"`: Plusieurs users, plusieurs brands

### Trial Configuration
- **Durée**: 2 semaines par défaut
- **Features**: `websites`, `templates`, `analytics`
- **Slots**: 2 users, 1 brand (solo mode)
- **Extension**: Possible via `extend_trial_period()`

### Default Features
- `websites`: Feature principale
- `templates`: Templates IA  
- `analytics`: Analytics de base
- **Limite**: Illimitée pendant trial
- **Expiration**: Avec le trial

### Default Slots
- **Users**: 2 (admin + 1 invité)
- **Brands**: 1 (solo business)
- **Tracking**: Automatique via signaux

### Default Roles
- `company_admin`: Administration company
- `brand_admin`: Administration brand
- `websites_admin`: Administration feature websites

---

## Flow Complet

### 1. Vérification Éligibilité
```
GET /onboarding/business/check-eligibility/
→ Vérifie user.company is None + user.is_active
```

### 2. Setup Business
```
POST /onboarding/business/setup/
→ Crée Company + Brand + User assignment
→ Configure Slots, Features, Trial, Roles
→ Transaction atomique
```

### 3. Vérification Status
```
GET /onboarding/business/setup-status/
→ Status complet avec business_summary
```

### 4. Monitoring
```
GET /onboarding/business/stats/
→ Stats détaillées + usage slots + features
```

---

## Codes d'Erreur

| Code | Statut | Description |
|------|--------|-------------|
| 400 | Bad Request | User non éligible, données invalides |
| 401 | Unauthorized | Non authentifié |
| 403 | Forbidden | Permissions insuffisantes |
| 500 | Internal Error | Erreur lors création business |

---

## Configuration Requise

### Dépendances
- `company_core.models.Company`
- `brands_core.models.Brand`
- `company_slots.models.CompanySlots`
- `company_features.models.Feature, CompanyFeature` (optionnel)
- `billing_core.models.Plan, Subscription` (optionnel)
- `users_roles.models.Role, UserRole` (optionnel)
- `task_core.models.Task` (optionnel)

### Settings Celery
```python
# Configuration des tâches programmées
CELERY_BEAT_SCHEDULE = {
    'onboarding-daily-maintenance': {
        'task': 'onboarding_business.tasks.daily_onboarding_maintenance',
        'schedule': crontab(hour=8, minute=0),  # 8h tous les jours
    },
    'onboarding-weekly-cleanup': {
        'task': 'onboarding_business.tasks.cleanup_onboarding_data', 
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Dimanche 2h
    },
}
```

---

## Exemples d'Usage

### Setup Business Complet
```bash
# 1. Vérifier éligibilité
curl -X GET /onboarding/business/check-eligibility/ \
  -H "Authorization: Bearer <token>"

# 2. Créer business
curl -X POST /onboarding/business/setup/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"business_name": "Mon Super Business"}'

# 3. Vérifier status
curl -X GET /onboarding/business/setup-status/ \
  -H "Authorization: Bearer <token>"

# 4. Stats détaillées
curl -X GET /onboarding/business/stats/ \
  -H "Authorization: Bearer <token>"
```