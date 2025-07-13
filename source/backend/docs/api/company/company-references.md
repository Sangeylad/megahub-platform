# Company System - Référence Complète des Endpoints

## 🎯 Vue d'Ensemble des URLs

Le système company expose ses APIs sous la structure hiérarchique suivante :

```
/companies/                          # company_core
├── slots/                          # company_slots  
└── features/                       # company_features
    ├── available/                  # Catalogue features
    └── subscriptions/              # Abonnements company
```

## 📋 **COMPANY CORE** - `/companies/`

### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/` | Liste des entreprises | Filtrée par user |
| `POST` | `/companies/` | Créer entreprise | Superuser uniquement |
| `GET` | `/companies/{id}/` | Détail entreprise | Owner/superuser |
| `PUT` | `/companies/{id}/` | Mise à jour complète | Owner/superuser |
| `PATCH` | `/companies/{id}/` | Mise à jour partielle | Owner/superuser |
| `DELETE` | `/companies/{id}/` | Suppression (soft delete) | Owner/superuser |

### **Actions Custom**

#### **1. Check Limits** 📊

```http
POST /companies/{id}/check_limits/
Content-Type: application/json

{}
```

**Response Success** :
```json
{
    "company": "ACME Corp",
    "alerts_generated": 2,
    "alerts": [
        {
            "type": "brands_limit",
            "message": "Limite de marques atteinte (5/5)",
            "triggered_at": "2025-07-11T10:30:00Z"
        },
        {
            "type": "users_limit", 
            "message": "Limite d'utilisateurs atteinte (10/10)",
            "triggered_at": "2025-07-11T10:30:00Z"
        }
    ]
}
```

#### **2. Usage Stats** 📈

```http
GET /companies/{id}/usage_stats/
```

**Response** :
```json
{
    "slots": {
        "brands": {
            "total": 5,
            "used": 3,
            "percentage": 60.0,
            "available": 2
        },
        "users": {
            "total": 10,
            "used": 7,
            "percentage": 70.0,
            "available": 3
        }
    },
    "growth": {
        "brands_by_month": [
            {"month": "2025-06-01T00:00:00Z", "count": 2},
            {"month": "2025-07-01T00:00:00Z", "count": 1}
        ],
        "users_by_type": [
            {"user_type": "brand_admin", "count": 2},
            {"user_type": "brand_member", "count": 5}
        ]
    },
    "activity": {
        "total_brands": 3,
        "active_brands": 3,
        "total_users": 7,
        "recent_logins": 5
    }
}
```

#### **3. Upgrade Slots** 💰

```http
POST /companies/{id}/upgrade_slots/
Content-Type: application/json

{
    "brands_slots": 10,
    "users_slots": 20
}
```

**Response Success** :
```json
{
    "message": "Slots mis à jour avec succès",
    "brands_slots": 10,
    "users_slots": 20,
    "brands_available": 7,
    "users_available": 13
}
```

**Response Error** :
```json
{
    "error": "Impossible de réduire à 3 slots, 5 brands utilisées"
}
```

### **Filtres & Recherche**

```http
GET /companies/?is_active=true&search=acme&ordering=-created_at
```

**Paramètres Disponibles** :
- `is_active` : true/false
- `admin` : ID de l'admin
- `search` : Recherche dans name, billing_email, admin__username
- `ordering` : name, created_at, updated_at (avec - pour DESC)

### **Expansion des Relations**

```http
GET /companies/{id}/?expand=slots_info,subscription_info
```

**Paramètres expand** :
- `admin_details` : Détails complets de l'admin
- `slots_info` : Informations slots détaillées
- `subscription_info` : Informations abonnement

## 📦 **COMPANY SLOTS** - `/companies/slots/`

### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/slots/` | Liste des slots | Filtrée par company |
| `GET` | `/companies/slots/{id}/` | Détail slots | Company membre |
| `PUT` | `/companies/slots/{id}/` | Mise à jour slots | Company admin |
| `PATCH` | `/companies/slots/{id}/` | Mise à jour partielle | Company admin |

### **Actions Custom**

#### **1. Refresh Counts** 🔄

```http
POST /companies/slots/{id}/refresh-counts/
Content-Type: application/json

{}
```

**Response** :
```json
{
    "message": "Compteurs mis à jour avec succès",
    "slots": {
        "id": 1,
        "company_name": "ACME Corp",
        "brands_slots": 5,
        "users_slots": 10,
        "current_brands_count": 3,
        "current_users_count": 7,
        "brands_usage_percentage": 60.0,
        "users_usage_percentage": 70.0,
        "available_brands_slots": 2,
        "available_users_slots": 3,
        "is_brands_limit_reached": false,
        "is_users_limit_reached": false
    }
}
```

#### **2. Usage Alerts** ⚠️

```http
GET /companies/slots/{id}/usage-alerts/
```

**Response** :
```json
{
    "company": "ACME Corp",
    "alerts_count": 2,
    "alerts": [
        {
            "type": "brands_warning",
            "severity": "warning",
            "message": "Limite de marques bientôt atteinte (4/5)",
            "percentage": 80.0
        },
        {
            "type": "users_limit",
            "severity": "error",
            "message": "Limite d'utilisateurs atteinte (10/10)",
            "percentage": 100.0
        }
    ]
}
```

#### **3. Increase Slots** 💰

```http
POST /companies/slots/{id}/increase-slots/
Content-Type: application/json

{
    "brands_increment": 5,
    "users_increment": 10
}
```

**Response** :
```json
{
    "message": "Slots augmentés avec succès",
    "changes": {
        "brands_slots": {
            "old": 5,
            "new": 10,
            "increment": 5
        },
        "users_slots": {
            "old": 10,
            "new": 20,
            "increment": 10
        }
    },
    "available_slots": {
        "brands": 7,
        "users": 13
    }
}
```

#### **4. Overview** 📊

```http
GET /companies/slots/overview/
Authorization: Bearer {superuser_token}
```

**Response** :
```json
{
    "total_slots": {
        "brands": 250,
        "users": 500
    },
    "total_used": {
        "brands": 180,
        "users": 350
    },
    "usage_percentages": {
        "brands": 72.0,
        "users": 70.0
    },
    "companies_near_limit": [
        {
            "company": "ACME Corp",
            "brands_percentage": 80.0,
            "users_percentage": 100.0
        }
    ],
    "companies_count": 25
}
```

### **Filtres & Recherche**

```http
GET /companies/slots/?company=1&ordering=-created_at
```

**Paramètres** :
- `company` : ID de l'entreprise
- `search` : Recherche dans company__name
- `ordering` : brands_slots, users_slots, created_at

## 🎯 **COMPANY FEATURES** - `/companies/features/`

### **Features Disponibles** - `/companies/features/available/`

#### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/features/available/` | Catalogue features | Authenticated |
| `POST` | `/companies/features/available/` | Créer feature | Admin uniquement |
| `GET` | `/companies/features/available/{id}/` | Détail feature | Authenticated |
| `PUT` | `/companies/features/available/{id}/` | Mise à jour feature | Admin uniquement |
| `DELETE` | `/companies/features/available/{id}/` | Suppression feature | Admin uniquement |

#### **Exemple GET Liste Features**

```http
GET /companies/features/available/?feature_type=websites&is_premium=false
```

**Response** :
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "name": "basic_websites",
            "display_name": "Sites Web Basiques",
            "description": "Création de sites web avec templates",
            "feature_type": "websites",
            "is_active": true,
            "is_premium": false,
            "sort_order": 1,
            "subscribed_companies_count": 45
        },
        {
            "id": 2,
            "name": "ai_templates",
            "display_name": "Templates IA",
            "description": "Génération de contenu avec IA",
            "feature_type": "templates",
            "is_active": true,
            "is_premium": true,
            "sort_order": 2,
            "subscribed_companies_count": 23
        }
    ]
}
```

#### **Filtres Features**

```http
GET /companies/features/available/?feature_type=websites&is_active=true&is_premium=false&search=template
```

**Paramètres** :
- `feature_type` : websites, templates, tasks, analytics, crm, integrations
- `is_active` : true/false
- `is_premium` : true/false
- `search` : Recherche dans name, display_name, description
- `ordering` : sort_order, display_name, created_at

### **Abonnements Features** - `/companies/features/subscriptions/`

#### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/features/subscriptions/` | Features de la company | Company membre |
| `POST` | `/companies/features/subscriptions/` | S'abonner à feature | Company admin |
| `GET` | `/companies/features/subscriptions/{id}/` | Détail abonnement | Company membre |
| `PUT` | `/companies/features/subscriptions/{id}/` | Mise à jour abonnement | Company admin |
| `DELETE` | `/companies/features/subscriptions/{id}/` | Se désabonner | Company admin |

#### **Exemple POST Abonnement**

```http
POST /companies/features/subscriptions/
Content-Type: application/json

{
    "company": 1,
    "feature": 3,
    "is_enabled": true,
    "usage_limit": 100,
    "expires_at": "2025-12-31T23:59:59Z"
}
```

**Response** :
```json
{
    "id": 15,
    "company": 1,
    "company_name": "ACME Corp",
    "feature": 3,
    "feature_name": "Templates IA Premium",
    "feature_type": "templates",
    "is_enabled": true,
    "usage_limit": 100,
    "current_usage": 0,
    "subscribed_at": "2025-07-11T10:30:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "is_active_status": true,
    "usage_percentage": 0.0,
    "is_usage_limit_reached_status": false,
    "days_until_expiry": 173
}
```

### **Actions Custom Abonnements**

#### **1. Increment Usage** 📈

```http
POST /companies/features/subscriptions/{id}/increment-usage/
Content-Type: application/json

{
    "amount": 5
}
```

**Response Success** :
```json
{
    "message": "Utilisation incrémentée de 5",
    "current_usage": 45,
    "usage_limit": 100,
    "usage_percentage": 45.0,
    "limit_reached": false
}
```

**Response Error** :
```json
{
    "error": "Limite d'utilisation atteinte (100)"
}
```

#### **2. Reset Usage** 🔄

```http
POST /companies/features/subscriptions/{id}/reset-usage/
Content-Type: application/json

{}
```

**Response** :
```json
{
    "message": "Utilisation remise à zéro",
    "old_usage": 45,
    "current_usage": 0
}
```

#### **3. Toggle Enabled** 🔄

```http
POST /companies/features/subscriptions/{id}/toggle-enabled/
Content-Type: application/json

{}
```

**Response** :
```json
{
    "message": "Feature activée",
    "is_enabled": true,
    "is_active": true
}
```

#### **4. By Company** 🏢

```http
GET /companies/features/subscriptions/by-company/?company_id=1
```

**Response** :
```json
{
    "company_id": 1,
    "features_by_type": {
        "websites": [
            {
                "id": 10,
                "feature_name": "Sites Web Basiques",
                "is_enabled": true,
                "usage_info": {
                    "unlimited": false,
                    "current": 3,
                    "limit": 10,
                    "percentage": 30.0,
                    "limit_reached": false
                }
            }
        ],
        "templates": [
            {
                "id": 11,
                "feature_name": "Templates IA",
                "is_enabled": true,
                "usage_info": {
                    "unlimited": true
                }
            }
        ]
    },
    "total_features": 2,
    "active_features": 2
}
```

#### **5. Usage Stats** 📊

```http
GET /companies/features/subscriptions/usage-stats/
```

**Response** :
```json
{
    "global_stats": {
        "total_features": 150,
        "active_features": 120,
        "over_limit_features": 5,
        "activation_rate": 80.0
    },
    "stats_by_type": {
        "websites": {
            "total": 50,
            "active": 45,
            "over_limit": 2,
            "total_usage": 1250
        },
        "templates": {
            "total": 30,
            "active": 28,
            "over_limit": 1,
            "total_usage": 890
        }
    }
}
```

#### **6. Companies Overview** 🏢📊

```http
GET /companies/features/subscriptions/companies-overview/
Authorization: Bearer {superuser_token}
```

**Response** :
```json
{
    "companies_count": 50,
    "companies": [
        {
            "company_id": 1,
            "company_name": "ACME Corp",
            "total_features": 5,
            "active_features": 4,
            "premium_features": 2,
            "features_expiring_soon": 1,
            "features_over_limit": 0
        }
    ]
}
```

### **Filtres Abonnements**

```http
GET /companies/features/subscriptions/?company=1&feature=3&is_enabled=true&ordering=-created_at
```

**Paramètres** :
- `company` : ID de l'entreprise
- `feature` : ID de la feature
- `is_enabled` : true/false
- `search` : Recherche dans company__name, feature__display_name
- `ordering` : created_at, expires_at

## 🔐 **Codes de Statut HTTP**

### **Success Responses**

| Code | Description | Usage |
|------|-------------|-------|
| `200` | OK | GET, PUT, PATCH, actions custom |
| `201` | Created | POST création réussie |
| `204` | No Content | DELETE réussi |

### **Error Responses**

| Code | Description | Exemples |
|------|-------------|----------|
| `400` | Bad Request | Validation échouée, paramètres invalides |
| `401` | Unauthorized | Token manquant ou invalide |
| `403` | Forbidden | Permissions insuffisantes |
| `404` | Not Found | Ressource introuvable |
| `409` | Conflict | Contrainte unicité violée |
| `500` | Internal Server Error | Erreur serveur inattendue |

### **Exemples Error Responses**

#### **400 Bad Request - Validation**

```json
{
    "error": "Validation échouée",
    "details": {
        "brands_slots": ["Impossible de réduire à 3 slots, 5 brands utilisées"],
        "usage_limit": ["La limite ne peut pas être inférieure à l'utilisation actuelle (45)"]
    }
}
```

#### **403 Forbidden - Permissions**

```json
{
    "error": "Permission refusée",
    "message": "Seuls les administrateurs peuvent créer des entreprises"
}
```

#### **409 Conflict - Unicité**

```json
{
    "error": "Cette entreprise est déjà abonnée à cette feature"
}
```

## 🎯 **Endpoints par Cas d'Usage**

### **Setup Nouvelle Company**

```http
# 1. Créer company avec admin
POST /companies/
{
    "name": "ACME Corp",
    "billing_email": "billing@acme.com",
    "admin_username": "admin",
    "admin_email": "admin@acme.com",
    "admin_password": "securepass"
}

# 2. Vérifier slots créés automatiquement
GET /companies/slots/?company=1

# 3. Abonner aux features de base
POST /companies/features/subscriptions/
{
    "company": 1,
    "feature": 1,
    "usage_limit": 10
}
```

### **Monitoring Quotas Company**

```http
# 1. Stats globales company
GET /companies/1/usage_stats/

# 2. Alertes slots spécifiques
GET /companies/slots/1/usage-alerts/

# 3. Vérification limites
POST /companies/1/check_limits/
```

### **Upgrade Pay-per-Brand**

```http
# 1. Augmenter slots brands
POST /companies/slots/1/increase-slots/
{
    "brands_increment": 5
}

# 2. Vérifier nouvelles capacités
GET /companies/slots/1/

# 3. Refresh compteurs si nécessaire
POST /companies/slots/1/refresh-counts/
```

### **Analytics Plateforme**

```http
# 1. Vue d'ensemble slots (superuser)
GET /companies/slots/overview/

# 2. Stats features globales
GET /companies/features/subscriptions/usage-stats/

# 3. Overview companies features (superuser)
GET /companies/features/subscriptions/companies-overview/
```

Cette référence complète permet une **intégration API efficace** et un **monitoring précis** du système company dans MEGAHUB.