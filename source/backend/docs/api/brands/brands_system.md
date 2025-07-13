# Brands System - Référence Complète des Endpoints

## 🎯 Vue d'Ensemble des URLs

Le système brands expose ses APIs sous une structure simple et efficace :

```
/brands/                             # brands_core (seule app)
```

## 🏷️ **BRANDS CORE** - `/brands/`

### **Endpoints Standard REST**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/brands/` | Liste des marques | Filtrée par access |
| `POST` | `/brands/` | Créer marque | Company admin |
| `GET` | `/brands/{id}/` | Détail marque | Access required |
| `PUT` | `/brands/{id}/` | Mise à jour complète | Brand/Company admin |
| `PATCH` | `/brands/{id}/` | Mise à jour partielle | Brand/Company admin |
| `DELETE` | `/brands/{id}/` | Suppression (soft delete) | Company admin |

### **Actions Custom**

#### **1. Assign Users** 👥

```http
POST /brands/{id}/assign_users/
Content-Type: application/json

{
    "user_ids": [1, 2, 3]
}
```

**Validations** :
- Users doivent exister et être actifs
- Users doivent appartenir à la même company
- Au moins 1 user requis

**Response Success** :
```json
{
    "message": "Utilisateurs assignés avec succès",
    "brand": "ACME Brand",
    "assigned_users": 3,
    "total_users": 5
}
```

**Response Error** :
```json
{
    "user_ids": ["Certains utilisateurs n'existent pas"]
}
```

#### **2. Remove Users** 👥❌

```http
POST /brands/{id}/remove_users/
Content-Type: application/json

{
    "user_ids": [1, 2]
}
```

**Description** : Retire des utilisateurs d'une marque

**Response Success** :
```json
{
    "message": "Utilisateurs retirés avec succès",
    "brand": "ACME Brand",
    "removed_users": 2,
    "total_users": 3
}
```

**Response Error** :
```json
{
    "error": "user_ids est requis"
}
```

#### **3. Accessible Users** 👀

```http
GET /brands/{id}/accessible_users/
```

**Description** : Liste des utilisateurs ayant accès à cette marque

**Response** :
```json
{
    "brand": "ACME Brand",
    "users_count": 5,
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@acme.com",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "brand_admin",
            "is_brand_admin": true,
            "last_login": "2025-07-11T10:30:00Z"
        },
        {
            "id": 2,
            "username": "jane_doe",
            "email": "jane@acme.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "user_type": "brand_member",
            "is_brand_admin": false,
            "last_login": "2025-07-10T15:45:00Z"
        }
    ]
}
```

#### **4. Set Admin** 👑

```http
POST /brands/{id}/set_admin/
Content-Type: application/json

{
    "user_id": 1
}
```

**Description** : Définit l'admin d'une marque

**Validations** :
- User doit exister
- User doit appartenir à la même company
- User doit avoir accès à la brand

**Response Success** :
```json
{
    "message": "Admin de la marque mis à jour avec succès",
    "brand": "ACME Brand",
    "old_admin": "jane_admin",
    "new_admin": "john_admin"
}
```

**Side Effects** :
- Auto-add user à la marque si pas déjà assigné
- L'ancien admin reste assigné comme user normal

**Response Error** :
```json
{
    "error": "L'utilisateur doit appartenir à la même entreprise"
}
```

#### **5. Toggle Active** 🔄

```http
POST /brands/{id}/toggle_active/
Content-Type: application/json

{}
```

**Description** : Active/désactive une marque

**Response** :
```json
{
    "message": "Marque activée",
    "brand": "ACME Brand",
    "is_active": true
}
```

#### **6. By Company** 🏢

```http
GET /brands/by_company/?company_id=1
```

**Description** : Marques groupées par entreprise

**Query Params** :
- `company_id` (optional) : Filtrer par company ID

**Response** :
```json
{
    "brands_by_company": {
        "ACME Corp": [
            {
                "id": 1,
                "name": "ACME Brand",
                "company": 1,
                "company_name": "ACME Corp",
                "brand_admin_name": "John Doe",
                "url": "https://acme.com",
                "is_active": true,
                "users_count": 5,
                "created_at": "2025-07-01T00:00:00Z"
            },
            {
                "id": 2,
                "name": "ACME Pro",
                "company": 1,
                "company_name": "ACME Corp",
                "brand_admin_name": "Jane Doe",
                "url": "https://acmepro.com",
                "is_active": true,
                "users_count": 3,
                "created_at": "2025-07-05T00:00:00Z"
            }
        ]
    },
    "total_brands": 2,
    "companies_count": 1
}
```

#### **7. Recent Activity** 📈

```http
GET /brands/recent_activity/
```

**Description** : Activité récente sur les marques (7 derniers jours)

**Response** :
```json
{
    "recent_brands": [
        {
            "id": 1,
            "name": "New Brand",
            "company": 1,
            "company_name": "ACME Corp",
            "brand_admin_name": "John Doe",
            "url": "https://newbrand.com",
            "is_active": true,
            "users_count": 1,
            "created_at": "2025-07-10T14:30:00Z"
        }
    ],
    "updated_brands": [
        {
            "id": 2,
            "name": "Updated Brand",
            "company": 2,
            "company_name": "Widget Inc",
            "brand_admin_name": "Bob Smith",
            "url": "https://widget.com",
            "is_active": true,
            "users_count": 4,
            "created_at": "2025-07-01T00:00:00Z"
        }
    ],
    "total_recent": 5,
    "total_updated": 8
}
```

#### **8. Brands Overview** 📊

```http
GET /brands/brands_overview/
```

**Description** : Vue d'ensemble des marques avec analytics

**Response** :
```json
{
    "total_brands": 150,
    "active_brands": 140,
    "brands_with_admin": 130,
    "admin_rate": 86.7,
    "brands_by_company": [
        {"company__name": "ACME Corp", "count": 15},
        {"company__name": "Widget Inc", "count": 12},
        {"company__name": "Tech Solutions", "count": 10}
    ],
    "top_brands": [
        {
            "id": 1,
            "name": "Top Brand",
            "company": 1,
            "company_name": "ACME Corp",
            "brand_admin_name": "John Doe",
            "url": "https://topbrand.com",
            "is_active": true,
            "users_count": 25,
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

### **Filtres & Recherche**

```http
GET /brands/?company=1&brand_admin=5&is_active=true&search=acme&ordering=-created_at
```

**Paramètres Disponibles** :
- `company` : ID de l'entreprise
- `brand_admin` : ID de l'admin de la marque
- `is_active` : true/false
- `search` : Recherche dans name, description, company__name
- `ordering` : name, created_at, updated_at (avec - pour DESC)

### **Expansion des Relations**

```http
GET /brands/{id}/?expand=users_list,recent_activity
```

**Paramètres expand** :
- `users_list` : Liste détaillée des utilisateurs avec accès
- `recent_activity` : Activité récente sur la marque

**Response avec expansion** :
```json
{
    "id": 1,
    "name": "ACME Brand",
    "company_name": "ACME Corp",
    "brand_admin_details": {
        "id": 5,
        "username": "john_admin",
        "email": "john@acme.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "accessible_users_count": 5,
    "websites_count": 12,
    "templates_count": 8,
    "users_list": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@acme.com",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "brand_admin",
            "is_brand_admin": true
        }
    ],
    "recent_activity": {
        "last_website_update": null,
        "last_template_created": null,
        "last_user_activity": null
    }
}
```

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
| `400` | Bad Request | Validation échouée, quotas brands atteints |
| `401` | Unauthorized | Token manquant ou invalide |
| `403` | Forbidden | Permissions insuffisantes |
| `404` | Not Found | Brand introuvable |
| `409` | Conflict | Nom brand déjà utilisé dans la company |
| `500` | Internal Server Error | Erreur serveur inattendue |

### **Exemples Error Responses**

#### **400 Bad Request - Quotas Brands**

```json
{
    "non_field_errors": [
        "Limite de marques atteinte (5/5). Veuillez upgrader votre plan ou supprimer des marques existantes."
    ]
}
```

#### **403 Forbidden - Permissions**

```json
{
    "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

#### **409 Conflict - Nom Existant**

```json
{
    "name": ["Une marque avec ce nom existe déjà dans cette entreprise"]
}
```

## 🎯 **Endpoints par Cas d'Usage**

### **Setup Nouvelle Brand**

```http
# 1. Vérifier quotas disponibles
GET /companies/1/usage_stats/

# 2. Créer brand avec admin
POST /brands/
{
    "company": 1,
    "name": "Nouvelle Brand",
    "description": "Description de la marque",
    "url": "https://nouvelle-brand.com",
    "brand_admin": 42
}

# 3. Assigner utilisateurs supplémentaires
POST /brands/1/assign_users/
{
    "user_ids": [10, 15, 20]
}
```

### **Gestion Access Control**

```http
# 1. Voir utilisateurs avec accès
GET /brands/1/accessible_users/

# 2. Changer admin de la brand
POST /brands/1/set_admin/
{
    "user_id": 15
}

# 3. Retirer accès utilisateurs
POST /brands/1/remove_users/
{
    "user_ids": [10, 20]
}

# 4. Désactiver temporairement
POST /brands/1/toggle_active/
```

### **Analytics & Monitoring**

```http
# 1. Vue d'ensemble toutes brands
GET /brands/brands_overview/

# 2. Brands par company
GET /brands/by_company/?company_id=1

# 3. Activité récente
GET /brands/recent_activity/

# 4. Détail brand avec stats
GET /brands/1/?expand=users_list,recent_activity
```

### **Multi-Company Management**

```http
# 1. Toutes brands toutes companies (superuser)
GET /brands/

# 2. Brands d'une company spécifique
GET /brands/?company=1

# 3. Brands par admin
GET /brands/?brand_admin=5

# 4. Recherche cross-company
GET /brands/?search=tech&ordering=company__name
```

## 🔄 **Integration avec Company System**

### **Validation Quotas Pay-per-Brand**

```http
# Validation automatique lors de la création
POST /brands/
{
    "company": 1,
    "name": "Test Brand"
}

# Si quotas atteints
HTTP 400 Bad Request
{
    "non_field_errors": [
        "Limite de marques atteinte (5/5). Veuillez upgrader votre plan ou supprimer des marques existantes."
    ]
}

# Upgrade nécessaire
POST /companies/slots/1/increase-slots/
{
    "brands_increment": 5
}
```

### **Auto-Update CompanySlots**

```http
# Création brand → auto-update company.slots.current_brands_count
POST /brands/
{...}
# Side effect: company.slots.update_brands_count()

# Suppression brand → auto-update company.slots.current_brands_count  
DELETE /brands/1/
# Side effect: company.slots.update_brands_count()
```

### **Business Mode Impact**

```http
# Impact sur company.get_business_mode()
GET /companies/1/usage_stats/
{
    "business_mode": "agency",  # Détecté via brands.count() >= 2
    "brands": {
        "current": 3,
        "limit": 5
    }
}
```

## 🔒 **Sécurité & Permissions**

### **Brand-Scoped Access Control**

```python
# Filtrage automatique par accès
GET /brands/  # User voit seulement ses brands accessibles

# Company admin → toutes brands de sa company
# Brand admin → brands où il est admin + brands assignées
# Brand member → brands assignées
# Superuser → toutes brands
```

### **Soft Delete Protection**

```http
# DELETE = soft delete (is_deleted=True)
DELETE /brands/1/

# Brand reste en base mais filtrée automatiquement
GET /brands/  # N'inclut pas les brands soft deleted
```

### **Multi-Tenant Validation**

```http
# Validation automatique same-company
POST /brands/1/assign_users/
{
    "user_ids": [999]  # User d'une autre company
}

HTTP 400 Bad Request
{
    "user_ids": ["L'utilisateur user999 n'appartient pas à la même entreprise"]
}
```

Cette référence complète permet une **intégration API efficace** et une **gestion sécurisée des marques clientes** dans l'écosystème multi-tenant de MEGAHUB.