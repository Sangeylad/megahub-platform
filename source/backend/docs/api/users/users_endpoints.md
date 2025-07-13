# Users System - Référence Complète des Endpoints

## 🎯 Vue d'Ensemble des URLs

Le système users expose ses APIs sous la structure hiérarchique suivante :

```
/users/                              # users_core
├── roles/                          # users_roles (Role management)
├── permissions/                    # users_roles (Permission catalog)
└── user-roles/                     # users_roles (Role assignments)
```

## 👤 **USERS CORE** - `/users/`

### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/users/` | Liste des utilisateurs | Filtrée par company |
| `POST` | `/users/` | Créer utilisateur | Company/Brand admin |
| `GET` | `/users/{id}/` | Détail utilisateur | Company membre |
| `PUT` | `/users/{id}/` | Mise à jour complète | Self/Company admin |
| `PATCH` | `/users/{id}/` | Mise à jour partielle | Self/Company admin |
| `DELETE` | `/users/{id}/` | Désactivation utilisateur | Company admin |

### **Actions Custom**

#### **1. Change Password** 🔐

```http
POST /users/{id}/change_password/
Content-Type: application/json

{
    "current_password": "oldpass123",
    "new_password": "newpass456",
    "new_password_confirm": "newpass456"
}
```

**Permissions** : Self ou Company admin

**Response Success** :
```json
{
    "message": "Mot de passe changé avec succès",
    "user": "john_doe"
}
```

**Response Error** :
```json
{
    "current_password": ["Le mot de passe actuel est incorrect"]
}
```

#### **2. Assign Brands** 🏷️

```http
POST /users/{id}/assign_brands/
Content-Type: application/json

{
    "brand_ids": [1, 2, 3]
}
```

**Validations** :
- Brands doivent exister et être actives
- Brands doivent appartenir à la même company
- User doit appartenir à la même company

**Response Success** :
```json
{
    "message": "Marques assignées avec succès",
    "user": "john_doe",
    "assigned_brands": 3,
    "total_brands": 5
}
```

#### **3. Accessible Brands** 👀

```http
GET /users/{id}/accessible_brands/
```

**Response** :
```json
{
    "user": "john_doe",
    "brands_count": 3,
    "brands": [
        {
            "id": 1,
            "name": "ACME Brand",
            "company": "ACME Corp",
            "is_admin": true,
            "is_active": true,
            "url": "https://acme.com",
            "users_count": 5
        },
        {
            "id": 2,
            "name": "ACME Pro",
            "company": "ACME Corp",
            "is_admin": false,
            "is_active": true,
            "url": "https://acmepro.com",
            "users_count": 3
        }
    ]
}
```

#### **4. Toggle Active** 🔄

```http
POST /users/{id}/toggle_active/
Content-Type: application/json

{}
```

**Protection** : Empêche de désactiver l'admin de l'entreprise

**Response Success** :
```json
{
    "message": "Utilisateur activé",
    "user": "john_doe",
    "is_active": true
}
```

**Response Error (Admin)** :
```json
{
    "error": "Impossible de désactiver l'admin de l'entreprise"
}
```

#### **5. Promote to Brand Admin** 👑

```http
POST /users/{id}/promote_to_brand_admin/
Content-Type: application/json

{
    "brand_id": 1
}
```

**Validations** :
- Brand doit exister
- User doit avoir accès à cette brand
- Brand doit appartenir à la même company

**Response Success** :
```json
{
    "message": "Utilisateur promu admin de la marque",
    "user": "john_doe",
    "brand": "ACME Brand",
    "old_admin": "jane_admin"
}
```

#### **6. By Company** 🏢

```http
GET /users/by_company/?company_id=1
```

**Query Params** :
- `company_id` (optional) : Filtrer par company ID

**Response** :
```json
{
    "users_by_company": {
        "ACME Corp": [
            {
                "id": 1,
                "username": "john_doe",
                "email": "john@acme.com",
                "user_type": "brand_admin",
                "accessible_brands_count": 3,
                "is_active": true
            },
            {
                "id": 2,
                "username": "jane_doe",
                "email": "jane@acme.com",
                "user_type": "brand_member",
                "accessible_brands_count": 1,
                "is_active": true
            }
        ]
    },
    "total_users": 25,
    "companies_count": 1
}
```

#### **7. By Type** 📊

```http
GET /users/by_type/
```

**Response** :
```json
{
    "users_by_type": {
        "Admin Agence": [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@acme.com",
                "company_name": "ACME Corp"
            }
        ],
        "Admin Marque": [
            {
                "id": 2,
                "username": "brand_admin",
                "email": "badmin@acme.com",
                "company_name": "ACME Corp"
            }
        ],
        "Membre Marque": [
            {
                "id": 3,
                "username": "member",
                "email": "member@acme.com",
                "company_name": "ACME Corp"
            }
        ]
    },
    "total_users": 25,
    "types_count": 3
}
```

#### **8. Recent Activity** 📈

```http
GET /users/recent_activity/
```

**Response** :
```json
{
    "recent_users": [
        {
            "id": 1,
            "username": "new_user",
            "email": "new@acme.com",
            "company_name": "ACME Corp",
            "date_joined": "2025-07-10T14:30:00Z"
        }
    ],
    "active_users": [
        {
            "id": 2,
            "username": "active_user",
            "email": "active@acme.com",
            "company_name": "ACME Corp",
            "last_login": "2025-07-11T09:15:00Z"
        }
    ],
    "total_recent": 5,
    "total_active": 8
}
```

#### **9. Users Overview** 🎯

```http
GET /users/users_overview/
```

**Response** :
```json
{
    "total_users": 150,
    "active_users": 140,
    "activation_rate": 93.3,
    "users_by_type": [
        {"user_type": "brand_member", "count": 80},
        {"user_type": "brand_admin", "count": 45},
        {"user_type": "agency_admin", "count": 15},
        {"user_type": "client_readonly", "count": 10}
    ],
    "users_by_company": [
        {"company__name": "ACME Corp", "count": 25},
        {"company__name": "Widget Inc", "count": 20}
    ],
    "top_users": [
        {
            "id": 1,
            "username": "super_user",
            "email": "super@acme.com",
            "brands_count": 15,
            "company_name": "ACME Corp"
        }
    ]
}
```

### **Filtres & Recherche**

```http
GET /users/?company=1&user_type=brand_admin&is_active=true&search=john&ordering=-date_joined
```

**Paramètres Disponibles** :
- `company` : ID de l'entreprise
- `user_type` : agency_admin, brand_admin, brand_member, client_readonly
- `is_active` : true/false
- `search` : Recherche dans username, email, first_name, last_name
- `ordering` : username, email, date_joined, last_login (avec - pour DESC)

### **Expansion des Relations**

```http
GET /users/{id}/?expand=brands_list,administered_brands_list
```

**Paramètres expand** :
- `brands_list` : Liste détaillée des marques accessibles
- `administered_brands_list` : Liste détaillée des marques administrées

## 🎭 **USERS ROLES** - `/users/roles/`, `/users/permissions/`, `/users/user-roles/`

### **Role Management** - `/users/roles/`

#### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/users/roles/` | Liste des rôles | Authenticated |
| `POST` | `/users/roles/` | Créer rôle | Admin seulement |
| `GET` | `/users/roles/{id}/` | Détail rôle | Authenticated |
| `PUT` | `/users/roles/{id}/` | Mise à jour rôle | Admin seulement |
| `DELETE` | `/users/roles/{id}/` | Suppression rôle | Admin seulement |

#### **Actions Custom**

### **1. Assign Permissions** 🔐

```http
POST /users/roles/{id}/assign-permissions/
Content-Type: application/json

{
    "permission_ids": [1, 2, 3, 4, 5],
    "is_granted": true
}
```

**Response** :
```json
{
    "message": "Permissions assignées avec succès",
    "role": "Brand Admin",
    "permissions_count": 5,
    "is_granted": true
}
```

### **2. Users with Role** 👥

```http
GET /users/roles/{id}/users/
```

**Response** :
```json
{
    "role": "Brand Admin",
    "users_count": 5,
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@acme.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "ACME Corp",
            "granted_at": "2025-07-01T00:00:00Z",
            "expires_at": null,
            "is_active": true,
            "context": {
                "company": "ACME Corp",
                "brand": "ACME Brand",
                "feature": null,
                "is_active": true,
                "expires_at": null
            }
        }
    ]
}
```

### **3. Role Permissions** 🔑

```http
GET /users/roles/{id}/permissions/
```

**Response** :
```json
{
    "role": "Brand Admin",
    "permissions_count": 8,
    "permissions": [
        {
            "id": 1,
            "name": "Websites Read",
            "permission_type": "read",
            "resource_type": "website",
            "is_granted": true,
            "created_at": "2025-07-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Websites Write",
            "permission_type": "write",
            "resource_type": "website",
            "is_granted": true,
            "created_at": "2025-07-01T00:00:00Z"
        }
    ]
}
```

### **Permission Catalog** - `/users/permissions/`

#### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/users/permissions/` | Liste permissions | Authenticated |
| `GET` | `/users/permissions/{id}/` | Détail permission | Authenticated |

#### **Actions Custom**

### **1. Roles with Permission** 🎭

```http
GET /users/permissions/{id}/roles/
```

**Response** :
```json
{
    "permission": "Websites Write",
    "roles_count": 3,
    "roles": [
        {
            "id": 1,
            "name": "Brand Admin",
            "role_type": "brand",
            "is_system": false,
            "users_count": 5,
            "assigned_at": "2025-07-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Company Admin",
            "role_type": "company",
            "is_system": true,
            "users_count": 2,
            "assigned_at": "2025-07-01T00:00:00Z"
        }
    ]
}
```

### **Role Assignments** - `/users/user-roles/`

#### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/users/user-roles/` | Liste assignations | Filtrée par company |
| `POST` | `/users/user-roles/` | Créer assignation | Company/Brand admin |
| `GET` | `/users/user-roles/{id}/` | Détail assignation | Company membre |
| `PUT` | `/users/user-roles/{id}/` | Mise à jour assignation | Granted_by/Admin |
| `DELETE` | `/users/user-roles/{id}/` | Suppression assignation | Granted_by/Admin |

#### **Exemple POST Création**

```http
POST /users/user-roles/
Content-Type: application/json

{
    "user": 15,
    "role": 5,
    "company": 1,
    "brand": 3,
    "expires_at": "2025-12-31T23:59:59Z"
}
```

**Response** :
```json
{
    "id": 25,
    "user": 15,
    "user_username": "john_doe",
    "user_email": "john@acme.com",
    "role": 5,
    "role_name": "Brand Admin",
    "role_type": "brand",
    "company": 1,
    "company_name": "ACME Corp",
    "brand": 3,
    "brand_name": "ACME Brand",
    "feature": null,
    "feature_name": null,
    "granted_by": 1,
    "granted_by_username": "admin",
    "granted_at": "2025-07-11T10:30:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "is_active_status": true,
    "context_summary": {
        "company": "ACME Corp",
        "brand": "ACME Brand",
        "feature": null,
        "is_active": true,
        "expires_at": "2025-12-31T23:59:59Z"
    }
}
```

#### **Actions Custom**

### **1. By User** 👤

```http
GET /users/user-roles/by-user/?user_id=1
```

**Response** :
```json
{
    "user_id": 1,
    "roles_by_context": {
        "brand - ACME Corp - ACME Brand": [
            {
                "id": 1,
                "role_name": "Brand Admin",
                "expires_at": null,
                "is_active_status": true,
                "context_summary": {
                    "company": "ACME Corp",
                    "brand": "ACME Brand"
                }
            }
        ],
        "company - ACME Corp": [
            {
                "id": 2,
                "role_name": "Analytics Viewer",
                "expires_at": "2025-12-31T23:59:59Z",
                "is_active_status": true,
                "context_summary": {
                    "company": "ACME Corp"
                }
            }
        ]
    },
    "total_roles": 3,
    "active_roles": 3
}
```

### **2. By Role** 🎭

```http
GET /users/user-roles/by-role/?role_id=1
```

**Response** :
```json
{
    "role_id": 1,
    "assignments_by_company": {
        "ACME Corp": [
            {
                "user_username": "john_doe",
                "user_email": "john@acme.com",
                "granted_at": "2025-07-01T00:00:00Z",
                "context_summary": {
                    "company": "ACME Corp",
                    "brand": "ACME Brand"
                }
            }
        ],
        "Widget Inc": [
            {
                "user_username": "jane_doe",
                "user_email": "jane@widget.com",
                "granted_at": "2025-07-05T00:00:00Z",
                "context_summary": {
                    "company": "Widget Inc",
                    "brand": "Widget Pro"
                }
            }
        ]
    },
    "total_assignments": 5,
    "active_assignments": 5
}
```

### **3. Expiring Soon** ⏰

```http
GET /users/user-roles/expiring-soon/
```

**Response** :
```json
{
    "expiring_roles_count": 3,
    "expiring_roles": [
        {
            "id": 15,
            "user_username": "john_doe",
            "user_email": "john@acme.com",
            "role_name": "Temporary Access",
            "expires_at": "2025-07-15T23:59:59Z",
            "context_summary": {
                "company": "ACME Corp",
                "brand": "ACME Brand",
                "feature": null,
                "is_active": true,
                "expires_at": "2025-07-15T23:59:59Z"
            }
        }
    ]
}
```

### **4. User Permissions Overview** 🔍

```http
GET /users/user-roles/user-permissions-overview/?user_id=1
```

**Response** :
```json
{
    "user_id": 1,
    "user_username": "john_doe",
    "user_email": "john@acme.com",
    "total_roles": 3,
    "active_roles": 3,
    "total_permissions": 15,
    "permissions_by_type": {
        "read": [
            "websites_read",
            "analytics_read",
            "templates_read"
        ],
        "write": [
            "websites_write",
            "templates_write"
        ],
        "delete": [
            "websites_delete"
        ],
        "admin": [
            "brand_admin",
            "users_admin"
        ]
    }
}
```

### **5. Roles Overview** 📊

```http
GET /users/user-roles/roles-overview/
```

**Response** :
```json
{
    "total_assignments": 150,
    "active_assignments": 140,
    "activation_rate": 93.3,
    "assignments_by_role": [
        {"role__display_name": "Brand Member", "count": 80},
        {"role__display_name": "Brand Admin", "count": 45},
        {"role__display_name": "Company Admin", "count": 15},
        {"role__display_name": "Analytics Viewer", "count": 10}
    ],
    "assignments_by_type": [
        {"role__role_type": "brand", "count": 125},
        {"role__role_type": "company", "count": 20},
        {"role__role_type": "feature", "count": 5}
    ]
}
```

### **Filtres par App**

#### **Roles**
```http
GET /users/roles/?role_type=brand&is_active=true&is_system=false&search=admin&ordering=name
```

**Paramètres** :
- `role_type` : system, company, brand, feature
- `is_active` : true/false
- `is_system` : true/false
- `search` : Recherche dans name, display_name, description
- `ordering` : role_type, name, display_name, created_at

#### **Permissions**
```http
GET /users/permissions/?permission_type=write&resource_type=website&is_active=true&search=website&ordering=resource_type
```

**Paramètres** :
- `permission_type` : read, write, delete, admin
- `resource_type` : website, template, analytics, etc.
- `is_active` : true/false
- `search` : Recherche dans name, display_name, description
- `ordering` : resource_type, permission_type, name

#### **User Roles**
```http
GET /users/user-roles/?user=1&role=5&company=1&brand=3&feature=2&ordering=-granted_at
```

**Paramètres** :
- `user` : ID de l'utilisateur
- `role` : ID du rôle
- `company` : ID de l'entreprise (contexte)
- `brand` : ID de la marque (contexte)
- `feature` : ID de la feature (contexte)
- `search` : Recherche dans user__username, role__display_name, company__name, brand__name
- `ordering` : granted_at, expires_at, created_at

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
| `400` | Bad Request | Validation échouée, quotas atteints |
| `401` | Unauthorized | Token manquant ou invalide |
| `403` | Forbidden | Permissions insuffisantes |
| `404` | Not Found | Utilisateur/rôle introuvable |
| `409` | Conflict | Email/username déjà utilisé, assignation déjà existante |

### **Exemples Error Responses**

#### **400 Bad Request - Quotas**

```json
{
    "non_field_errors": [
        "Limite d'utilisateurs atteinte (10/10). Veuillez upgrader votre plan ou désactiver des utilisateurs existants."
    ]
}
```

#### **403 Forbidden - Admin Protection**

```json
{
    "error": "Impossible de désactiver l'admin de l'entreprise"
}
```

#### **409 Conflict - Assignation Existante**

```json
{
    "non_field_errors": [
        "Cette assignation de rôle existe déjà"
    ]
}
```

## 🎯 **Endpoints par Cas d'Usage**

### **Setup Nouveau User**

```http
# 1. Créer user avec validation quotas
POST /users/
{
    "username": "new_user",
    "email": "user@acme.com",
    "password": "securepass",
    "password_confirm": "securepass",
    "company": 1,
    "user_type": "brand_member"
}

# 2. Assigner brands
POST /users/15/assign_brands/
{
    "brand_ids": [1, 3]
}

# 3. Assigner rôles granulaires
POST /users/user-roles/
{
    "user": 15,
    "role": 5,
    "company": 1,
    "brand": 1
}
```

### **Gestion Permissions Granulaires**

```http
# 1. Voir permissions actuelles user
GET /users/user-roles/user-permissions-overview/?user_id=15

# 2. Créer nouveau rôle custom
POST /users/roles/
{
    "name": "custom_editor",
    "display_name": "Custom Editor",
    "role_type": "brand"
}

# 3. Assigner permissions au rôle
POST /users/roles/10/assign-permissions/
{
    "permission_ids": [1, 2, 5],
    "is_granted": true
}

# 4. Assigner rôle à user
POST /users/user-roles/
{
    "user": 15,
    "role": 10,
    "brand": 1,
    "expires_at": "2025-12-31T23:59:59Z"
}
```

### **Monitoring & Analytics**

```http
# 1. Vue d'ensemble users company
GET /users/users_overview/

# 2. Rôles expirant bientôt
GET /users/user-roles/expiring-soon/

# 3. Utilisateurs par type
GET /users/by_type/

# 4. Assignations par rôle
GET /users/user-roles/roles-overview/
```

Cette référence complète permet une **intégration API efficace** et une **gestion sophistiquée des permissions** dans l'écosystème multi-tenant de MEGAHUB.