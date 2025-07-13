# Company Slots - Documentation Complète

## 🎯 Objectif de l'App

**company_slots** implémente le système de quotas pay-per-brand de MEGAHUB. Elle gère les limites de brands et d'utilisateurs par entreprise avec tracking automatique et alertes d'usage.

## 📁 Structure de l'App

```
company_slots/
├── models/
│   └── slots.py                 # CompanySlots avec méthodes business
├── serializers/
│   └── slots_serializers.py     # Serializers avec validations quotas
├── views/
│   └── slots_views.py           # ViewSet avec analytics slots
└── urls.py                      # Routes REST
```

## 🏗️ Modèle de Données

### **CompanySlots** - Quotas & Pay-per-Brand

```python
class CompanySlots(TimestampedMixin):
    """Gestion des slots par entreprise - Système de facturation à l'unité"""
```

#### **Relation Company**

| Champ | Type | Description | Cascade |
|-------|------|-------------|---------|
| `company` | OneToOneField(Company) | Entreprise propriétaire | CASCADE |

#### **Slots Configurés (Payants)**

| Champ | Type | Description | Default | Validations |
|-------|------|-------------|---------|-------------|
| `brands_slots` | IntegerField | Nombre de brands maximum | 5 | MinValue(1) |
| `users_slots` | IntegerField | Nombre d'users maximum | 10 | MinValue(1) |

#### **Usage Actuel (Auto-calculé)**

| Champ | Type | Description | Auto-Update |
|-------|------|-------------|-------------|
| `current_brands_count` | IntegerField | Brands actuellement créées | Via `update_brands_count()` |
| `current_users_count` | IntegerField | Users actuellement créés | Via `update_users_count()` |

#### **Métadonnées de Tracking**

| Champ | Type | Description | Usage |
|-------|------|-------------|-------|
| `last_brands_count_update` | DateTimeField | Dernière MAJ compteur brands | auto_now=True |
| `last_users_count_update` | DateTimeField | Dernière MAJ compteur users | auto_now=True |

#### **Indexes Optimisés**

```python
indexes = [
    models.Index(fields=['company']),
]
```

## 🔧 Méthodes Business

### **Update Automatique des Compteurs**

#### **Brands Count**

```python
def update_brands_count(self):
    """Met à jour le compteur de brands"""
    from brands_core.models.brand import Brand
    self.current_brands_count = Brand.objects.filter(
        company=self.company,
        is_deleted=False
    ).count()
    self.save(update_fields=['current_brands_count', 'last_brands_count_update'])
```

#### **Users Count**

```python
def update_users_count(self):
    """Met à jour le compteur d'utilisateurs"""
    from users_core.models.user import CustomUser
    self.current_users_count = CustomUser.objects.filter(
        company=self.company,
        is_active=True
    ).count()
    self.save(update_fields=['current_users_count', 'last_users_count_update'])
```

### **Calculs de Pourcentages**

```python
def get_brands_usage_percentage(self):
    """Pourcentage d'utilisation des slots brands"""
    if self.brands_slots == 0:
        return 0
    return round((self.current_brands_count / self.brands_slots) * 100, 2)

def get_users_usage_percentage(self):
    """Pourcentage d'utilisation des slots users"""
    if self.users_slots == 0:
        return 0
    return round((self.current_users_count / self.users_slots) * 100, 2)
```

### **Vérification des Limites**

```python
def is_brands_limit_reached(self):
    """Vérifie si la limite de brands est atteinte"""
    return self.current_brands_count >= self.brands_slots

def is_users_limit_reached(self):
    """Vérifie si la limite d'utilisateurs est atteinte"""
    return self.current_users_count >= self.users_slots
```

### **Calcul des Slots Disponibles**

```python
def get_available_brands_slots(self):
    """Nombre de slots brands disponibles"""
    return max(0, self.brands_slots - self.current_brands_count)

def get_available_users_slots(self):
    """Nombre de slots users disponibles"""
    return max(0, self.users_slots - self.current_users_count)
```

### **String Representation**

```python
def __str__(self):
    return f"Slots - {self.company.name} (B:{self.current_brands_count}/{self.brands_slots}, U:{self.current_users_count}/{self.users_slots})"
```

**Exemple Output** : `"Slots - ACME Corp (B:3/5, U:7/10)"`

## 📝 Serializers

### **CompanySlotsSerializer** - Serializer Principal

```python
class CompanySlotsSerializer(serializers.ModelSerializer):
    """Serializer pour CompanySlots avec champs calculés"""
```

#### **Champs Standard**

```python
fields = [
    'id', 'company', 'company_name',
    'brands_slots', 'users_slots',
    'current_brands_count', 'current_users_count',
    'brands_usage_percentage', 'users_usage_percentage',
    'available_brands_slots', 'available_users_slots',
    'is_brands_limit_reached', 'is_users_limit_reached',
    'last_brands_count_update', 'last_users_count_update',
    'created_at', 'updated_at'
]
```

#### **Read-Only Fields**

```python
read_only_fields = [
    'current_brands_count', 'current_users_count',
    'last_brands_count_update', 'last_users_count_update',
    'created_at', 'updated_at'
]
```

#### **Champs Calculés**

| Champ | Type | Description | Méthode |
|-------|------|-------------|---------|
| `brands_usage_percentage` | Float | % utilisation brands | `obj.get_brands_usage_percentage()` |
| `users_usage_percentage` | Float | % utilisation users | `obj.get_users_usage_percentage()` |
| `available_brands_slots` | Integer | Slots brands disponibles | `obj.get_available_brands_slots()` |
| `available_users_slots` | Integer | Slots users disponibles | `obj.get_available_users_slots()` |
| `is_brands_limit_reached` | Boolean | Limite brands atteinte | `obj.is_brands_limit_reached()` |
| `is_users_limit_reached` | Boolean | Limite users atteinte | `obj.is_users_limit_reached()` |

#### **Informations Company**

```python
company_name = CharField(source='company.name', read_only=True)
```

#### **Validations**

```python
def validate_brands_slots(self, value):
    """Valide le nombre de slots brands"""
    if value < 1:
        raise ValidationError("Le nombre de slots brands doit être au moins 1")
    return value

def validate_users_slots(self, value):
    """Valide le nombre de slots users"""
    if value < 1:
        raise ValidationError("Le nombre de slots users doit être au moins 1")
    return value
```

### **CompanySlotsUpdateSerializer** - Mise à Jour Sécurisée

```python
class CompanySlotsUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour des slots avec validation usage"""
```

#### **Champs Modifiables**

```python
fields = ['brands_slots', 'users_slots']
```

#### **Validation Anti-Réduction**

```python
def validate(self, data):
    """Validation globale contre réduction en-dessous usage actuel"""
    instance = self.instance
    
    # Vérifier brands_slots
    if 'brands_slots' in data:
        if data['brands_slots'] < instance.current_brands_count:
            raise ValidationError({
                'brands_slots': f"Impossible de réduire à {data['brands_slots']} slots, "
                              f"{instance.current_brands_count} brands sont actuellement utilisées"
            })
    
    # Vérifier users_slots
    if 'users_slots' in data:
        if data['users_slots'] < instance.current_users_count:
            raise ValidationError({
                'users_slots': f"Impossible de réduire à {data['users_slots']} slots, "
                             f"{instance.current_users_count} utilisateurs sont actuellement actifs"
            })
    
    return data
```

### **CompanySlotsStatsSerializer** - Analytics & Alertes

```python
class CompanySlotsStatsSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques des slots avec alertes"""
```

#### **Champs Analytics**

```python
fields = [
    'company_name', 'usage_summary', 'warnings',
    'last_brands_count_update', 'last_users_count_update'
]
```

#### **Usage Summary**

```python
def get_usage_summary(self, obj):
    """Résumé d'utilisation complet"""
    return {
        'brands': {
            'used': obj.current_brands_count,
            'total': obj.brands_slots,
            'available': obj.get_available_brands_slots(),
            'percentage': obj.get_brands_usage_percentage(),
        },
        'users': {
            'used': obj.current_users_count,
            'total': obj.users_slots,
            'available': obj.get_available_users_slots(),
            'percentage': obj.get_users_usage_percentage(),
        }
    }
```

#### **Système d'Alertes**

```python
def get_warnings(self, obj):
    """Avertissements sur l'utilisation avec niveaux de sévérité"""
    warnings = []
    
    brands_percentage = obj.get_brands_usage_percentage()
    users_percentage = obj.get_users_usage_percentage()
    
    # Alertes brands
    if brands_percentage >= 100:
        warnings.append({
            'type': 'brands_limit',
            'message': 'Limite de marques atteinte',
            'severity': 'error'
        })
    elif brands_percentage >= 80:
        warnings.append({
            'type': 'brands_warning',
            'message': 'Limite de marques bientôt atteinte',
            'severity': 'warning'
        })
    
    # Alertes users
    if users_percentage >= 100:
        warnings.append({
            'type': 'users_limit',
            'message': "Limite d'utilisateurs atteinte",
            'severity': 'error'
        })
    elif users_percentage >= 80:
        warnings.append({
            'type': 'users_warning',
            'message': "Limite d'utilisateurs bientôt atteinte",
            'severity': 'warning'
        })
    
    return warnings
```

#### **Types d'Alertes**

| Type | Seuil | Sévérité | Description |
|------|-------|----------|-------------|
| `brands_warning` | ≥ 80% | `warning` | Limite brands bientôt atteinte |
| `brands_limit` | ≥ 100% | `error` | Limite brands atteinte |
| `users_warning` | ≥ 80% | `warning` | Limite users bientôt atteinte |
| `users_limit` | ≥ 100% | `error` | Limite users atteinte |

## 🌐 API Endpoints

### **CompanySlotsViewSet** - Gestion Slots

```python
# URL Base: /companies/slots/
router.register(r'', CompanySlotsViewSet, basename='company-slots')
```

#### **Endpoints Standard**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/slots/` | Liste slots | Filtrée par company |
| `GET` | `/companies/slots/{id}/` | Détail slots | Company membre |
| `PUT` | `/companies/slots/{id}/` | Mise à jour slots | Company admin |
| `PATCH` | `/companies/slots/{id}/` | Mise à jour partielle | Company admin |

**Note** : Pas de création/suppression car les slots sont auto-créés avec la company.

#### **Actions Custom**

### **1. Refresh Counts** 🔄

```python
POST /companies/slots/{id}/refresh-counts/
```

**Description** : Recalcule les compteurs de brands et users depuis la base

**Input** : Aucun body requis

**Process** :
1. `slots.update_brands_count()` - Recompte brands actives
2. `slots.update_users_count()` - Recompte users actifs
3. Mise à jour timestamps

**Output** :
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

### **2. Usage Alerts** ⚠️

```python
GET /companies/slots/{id}/usage-alerts/
```

**Description** : Vérifie les alertes d'utilisation avec seuils configurés

**Output** :
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

### **3. Increase Slots** 💰

```python
POST /companies/slots/{id}/increase-slots/
```

**Description** : Augmente les slots (pour les upgrades pay-per-brand)

**Input** :
```json
{
    "brands_increment": 5,  // Ajout de 5 slots brands
    "users_increment": 10   // Ajout de 10 slots users
}
```

**Validations** :
- Incréments doivent être positifs
- Au moins un incrément requis

**Output Succès** :
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

**Output Erreur** :
```json
{
    "error": "Les incréments doivent être positifs"
}
```

### **4. Overview** 📊

```python
GET /companies/slots/overview/
```

**Description** : Vue d'ensemble des slots de toutes les entreprises (superuser seulement)

**Permissions** : Superuser uniquement

**Output** :
```json
{
    "total_slots": {
        "brands": 250,      // Total slots brands toutes companies
        "users": 500        // Total slots users toutes companies
    },
    "total_used": {
        "brands": 180,      // Total brands utilisées
        "users": 350        // Total users utilisés
    },
    "usage_percentages": {
        "brands": 72.0,     // % global d'utilisation brands
        "users": 70.0       // % global d'utilisation users
    },
    "companies_near_limit": [
        {
            "company": "ACME Corp",
            "brands_percentage": 80.0,
            "users_percentage": 100.0
        },
        {
            "company": "Widget Inc",
            "brands_percentage": 90.0,
            "users_percentage": 85.0
        }
    ],
    "companies_count": 25
}
```

**Critères "Near Limit"** : Companies avec brands ≥ 80% OU users ≥ 80%

## 🔐 Permissions & Sécurité

### **Niveaux d'Accès**

```python
def get_queryset(self):
    """Filtre selon les permissions utilisateur"""
    user = self.request.user
    
    # Superuser voit tout
    if user.is_superuser:
        return queryset
    
    # Company admin ne voit que son entreprise
    if user.is_company_admin():
        return queryset.filter(company=user.company)
    
    # Autres utilisateurs ne voient que leur entreprise
    if user.company:
        return queryset.filter(company=user.company)
    
    return queryset.none()
```

### **Intégration Billing Service**

```python
def perform_update(self, serializer):
    """Mise à jour avec validation et alertes"""
    slots = serializer.save()
    
    # Vérifier les alertes après mise à jour
    from billing_core.services.billing_service import BillingService
    BillingService.check_usage_limits(slots.company)
    
    return slots
```

## 🔧 Configuration & Filtres

### **Filtres Disponibles**

```python
filterset_fields = ['company']
search_fields = ['company__name']
ordering_fields = ['brands_slots', 'users_slots', 'created_at']
ordering = ['-created_at']
```

### **Optimisations Queryset**

```python
queryset = CompanySlots.objects.select_related('company').all()
```

## 🎯 Workflows Typiques

### **1. Création Automatique**

```python
# Lors de la création d'une Company
from company_slots.models.slots import CompanySlots

CompanySlots.objects.create(
    company=company,
    brands_slots=5,     # Plan de base
    users_slots=10      # Plan de base
)
```

### **2. Validation avant Ajout Brand**

```python
# Dans brands_core avant création
if not company.can_add_brand():
    raise ValidationError("Limite de brands atteinte")

# Après création brand
company.slots.update_brands_count()
```

### **3. Upgrade Pay-per-Brand**

```python
# Client achète +5 brands
POST /companies/slots/{id}/increase-slots/
{
    "brands_increment": 5
}

# Result: brands_slots 5 → 10, available +5
```

### **4. Monitoring & Alertes**

```python
# Check quotidien des companies proches limite
GET /companies/slots/overview/

# Pour chaque company ≥ 80%:
GET /companies/slots/{id}/usage-alerts/
# → Envoi emails d'alerte si nécessaire
```

Ce système garantit un **contrôle strict des quotas**, une **facturation précise pay-per-brand**, et un **monitoring proactif** de l'usage pour anticiper les besoins d'upgrade des clients MEGAHUB.