# Company Features - Documentation Complète

## 🎯 Objectif de l'App

**company_features** gère le système d'abonnement aux fonctionnalités de MEGAHUB. Elle permet aux entreprises de souscrire à des features spécifiques avec tracking d'usage et limites configurables.

## 📁 Structure de l'App

```
company_features/
├── models/
│   └── features.py              # Feature, CompanyFeature, FeatureUsageLog
├── serializers/
│   └── features_serializers.py  # Serializers avec stats usage
├── views/
│   └── features_views.py        # ViewSets avec analytics
└── urls.py                      # Routes avec namespaces
```

## 🏗️ Modèles de Données

### **Feature** - Catalogue des Fonctionnalités

```python
class Feature(TimestampedMixin):
    """Features disponibles sur la plateforme"""
```

#### **Champs Principaux**

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `name` | CharField(100) | Nom technique unique | Required, unique |
| `display_name` | CharField(150) | Nom d'affichage | Required |
| `description` | TextField | Description détaillée | Required |
| `feature_type` | CharField(20) | Type de feature | Choices |
| `is_active` | BooleanField | Feature disponible | Default: True |
| `is_premium` | BooleanField | Feature premium (payante) | Default: False |
| `sort_order` | IntegerField | Ordre d'affichage | Default: 0 |

#### **Feature Types** - Choix Disponibles

```python
FEATURE_TYPES = [
    ('websites', 'Sites Web'),
    ('templates', 'Templates IA'),
    ('tasks', 'Gestion de tâches'),
    ('analytics', 'Analytics'),
    ('crm', 'CRM'),
    ('integrations', 'Intégrations'),
]
```

#### **Indexes Optimisés**

```python
indexes = [
    models.Index(fields=['is_active']),
    models.Index(fields=['is_premium']),
    models.Index(fields=['feature_type']),
]
```

### **CompanyFeature** - Abonnements Features

```python
class CompanyFeature(TimestampedMixin):
    """Association entre Company et Features - Gestion des abonnements features"""
```

#### **Relations**

| Champ | Type | Description | Cascade |
|-------|------|-------------|---------|
| `company` | ForeignKey(Company) | Entreprise abonnée | CASCADE |
| `feature` | ForeignKey(Feature) | Feature souscrite | CASCADE |

#### **Configuration par Entreprise**

| Champ | Type | Description | Default |
|-------|------|-------------|---------|
| `is_enabled` | BooleanField | Feature activée pour cette entreprise | True |
| `usage_limit` | IntegerField | Limite d'utilisation (null=illimité) | None |
| `current_usage` | IntegerField | Utilisation actuelle | 0 |

#### **Dates d'Abonnement**

| Champ | Type | Description | Auto |
|-------|------|-------------|------|
| `subscribed_at` | DateTimeField | Date de souscription | auto_now_add |
| `expires_at` | DateTimeField | Date d'expiration | Optional |

#### **Contrainte Unicité**

```python
unique_together = ['company', 'feature']  # 1 abonnement par company/feature
```

#### **Indexes Optimisés**

```python
indexes = [
    models.Index(fields=['is_enabled']),
    models.Index(fields=['expires_at']),
    models.Index(fields=['company', 'is_enabled']),
]
```

### **Méthodes Business CompanyFeature**

#### **Statut d'Activation**

```python
def is_active(self):
    """Vérifie si la feature est active pour cette entreprise"""
    if not self.is_enabled or not self.feature.is_active:
        return False
    
    # Vérifier l'expiration
    if self.expires_at:
        return timezone.now() <= self.expires_at
    
    return True
```

#### **Gestion des Limites**

```python
def is_usage_limit_reached(self):
    """Vérifie si la limite d'utilisation est atteinte"""
    if self.usage_limit is None:
        return False
    return self.current_usage >= self.usage_limit

def get_usage_percentage(self):
    """Pourcentage d'utilisation de la feature"""
    if self.usage_limit is None:
        return 0
    if self.usage_limit == 0:
        return 100
    return round((self.current_usage / self.usage_limit) * 100, 2)
```

#### **Usage Tracking**

```python
def increment_usage(self, amount=1):
    """Incrémente l'utilisation de la feature"""
    self.current_usage += amount
    self.save(update_fields=['current_usage', 'updated_at'])

def reset_usage(self):
    """Remet à zéro l'utilisation (utile pour les limites mensuelles)"""
    self.current_usage = 0
    self.save(update_fields=['current_usage', 'updated_at'])
```

### **FeatureUsageLog** - Analytics Granulaires

```python
class FeatureUsageLog(TimestampedMixin):
    """Log d'utilisation des features - Pour analytics et facturation"""
```

#### **Relations**

| Champ | Type | Description | Cascade |
|-------|------|-------------|---------|
| `company_feature` | ForeignKey(CompanyFeature) | Feature utilisée | CASCADE |
| `user` | ForeignKey(CustomUser) | Utilisateur | SET_NULL |
| `brand` | ForeignKey(Brand) | Brand concernée | SET_NULL |

#### **Détails d'Utilisation**

| Champ | Type | Description | Default |
|-------|------|-------------|---------|
| `action` | CharField(100) | Action effectuée | Required |
| `quantity` | IntegerField | Quantité utilisée | 1 |
| `metadata` | JSONField | Données supplémentaires | {} |

#### **Actions Typiques**

```python
# Exemples d'actions trackées
actions = [
    'website_created',
    'ai_request',
    'template_generated',
    'page_published',
    'integration_sync',
    'analytics_report'
]
```

#### **Indexes Analytics**

```python
indexes = [
    models.Index(fields=['company_feature', 'created_at']),
    models.Index(fields=['user', 'created_at']),
    models.Index(fields=['action']),
]
```

## 📝 Serializers

### **FeatureSerializer** - Catalogue Features

```python
class FeatureSerializer(serializers.ModelSerializer):
    """Serializer pour Feature avec stats souscriptions"""
```

#### **Champs Standard**

```python
fields = [
    'id', 'name', 'display_name', 'description', 'feature_type',
    'is_active', 'is_premium', 'sort_order', 'created_at', 'updated_at',
    'subscribed_companies_count'
]
read_only_fields = ['created_at', 'updated_at']
```

#### **Champs Calculés**

```python
def get_subscribed_companies_count(self, obj):
    """Nombre d'entreprises abonnées à cette feature"""
    return obj.subscribed_companies.filter(is_enabled=True).count()
```

### **CompanyFeatureSerializer** - Abonnements Détaillés

```python
class CompanyFeatureSerializer(serializers.ModelSerializer):
    """Serializer pour CompanyFeature avec analytics"""
```

#### **Champs Standard**

```python
fields = [
    'id', 'company', 'company_name', 'feature', 'feature_name', 
    'feature_type', 'feature_description',
    'is_enabled', 'usage_limit', 'current_usage',
    'subscribed_at', 'expires_at',
    'is_active_status', 'usage_percentage', 'is_usage_limit_reached_status',
    'days_until_expiry', 'created_at', 'updated_at'
]
read_only_fields = ['subscribed_at', 'created_at', 'updated_at']
```

#### **Champs de Features (read-only)**

```python
feature_name = CharField(source='feature.display_name', read_only=True)
feature_type = CharField(source='feature.feature_type', read_only=True)
feature_description = CharField(source='feature.description', read_only=True)
company_name = CharField(source='company.name', read_only=True)
```

#### **Champs Calculés Avancés**

```python
def get_is_active_status(self, obj):
    """Statut d'activation de la feature"""
    return obj.is_active()

def get_usage_percentage(self, obj):
    """Pourcentage d'utilisation"""
    return obj.get_usage_percentage()

def get_is_usage_limit_reached_status(self, obj):
    """Limite d'utilisation atteinte"""
    return obj.is_usage_limit_reached()

def get_days_until_expiry(self, obj):
    """Nombre de jours avant expiration"""
    if not obj.expires_at:
        return None
    
    delta = obj.expires_at - timezone.now()
    return delta.days if delta.days > 0 else 0
```

### **CompanyFeatureListSerializer** - Vue Liste Optimisée

```python
fields = [
    'id', 'feature', 'feature_name', 'feature_type',
    'is_enabled', 'is_active_status', 'usage_info', 'expires_at'
]
```

#### **Usage Info Condensées**

```python
def get_usage_info(self, obj):
    """Informations d'utilisation condensées"""
    if obj.usage_limit is None:
        return {'unlimited': True}
    
    return {
        'unlimited': False,
        'current': obj.current_usage,
        'limit': obj.usage_limit,
        'percentage': obj.get_usage_percentage(),
        'limit_reached': obj.is_usage_limit_reached()
    }
```

### **CompanyFeatureCreateSerializer** - Création Abonnement

```python
fields = ['company', 'feature', 'is_enabled', 'usage_limit', 'expires_at']
```

#### **Validation Unicité**

```python
def validate(self, data):
    """Validation globale"""
    # Vérifier qu'il n'y a pas déjà une association
    if CompanyFeature.objects.filter(
        company=data['company'],
        feature=data['feature']
    ).exists():
        raise ValidationError(
            "Cette entreprise est déjà abonnée à cette feature"
        )
    
    return data
```

### **CompanyFeatureUpdateSerializer** - Mise à Jour Sécurisée

```python
fields = ['is_enabled', 'usage_limit', 'expires_at']
```

#### **Validation Limite vs Usage**

```python
def validate_usage_limit(self, value):
    """Valide que la nouvelle limite n'est pas inférieure à l'usage actuel"""
    if value is not None and self.instance:
        if value < self.instance.current_usage:
            raise ValidationError(
                f"La limite ne peut pas être inférieure à l'utilisation actuelle ({self.instance.current_usage})"
            )
    return value
```

### **Serializers Analytics**

#### **CompanyFeaturesOverviewSerializer**

```python
class CompanyFeaturesOverviewSerializer(serializers.Serializer):
    """Vue d'ensemble des features d'une entreprise"""
    
    company_id = IntegerField()
    company_name = CharField()
    total_features = IntegerField()
    active_features = IntegerField()
    premium_features = IntegerField()
    features_expiring_soon = IntegerField()  # 30 jours
    features_over_limit = IntegerField()
```

## 🌐 API Endpoints

### **URLs Structure**

```python
# URL Base: /companies/features/
router = DefaultRouter()
router.register(r'available', FeatureViewSet, basename='feature')
router.register(r'subscriptions', CompanyFeatureViewSet, basename='company-feature')
```

#### **Résolution URLs**

- `/companies/features/available/` → Catalogue features
- `/companies/features/subscriptions/` → Abonnements company

### **FeatureViewSet** - Catalogue Features

#### **Endpoints Standard**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/features/available/` | Liste features disponibles | Authenticated |
| `POST` | `/companies/features/available/` | Créer feature | Admin seulement |
| `GET` | `/companies/features/available/{id}/` | Détail feature | Authenticated |
| `PUT` | `/companies/features/available/{id}/` | Mise à jour feature | Admin seulement |
| `DELETE` | `/companies/features/available/{id}/` | Suppression feature | Admin seulement |

#### **Filtres & Recherche**

```python
filterset_fields = ['feature_type', 'is_active', 'is_premium']
search_fields = ['name', 'display_name', 'description']
ordering_fields = ['sort_order', 'display_name', 'created_at']
ordering = ['sort_order', 'display_name']
```

#### **Queryset Filtré**

```python
def get_queryset(self):
    """Tous les utilisateurs peuvent voir les features actives"""
    return super().get_queryset().filter(is_active=True)
```

### **CompanyFeatureViewSet** - Abonnements Features

#### **Endpoints Standard**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/features/subscriptions/` | Features company | Company membre |
| `POST` | `/companies/features/subscriptions/` | S'abonner à feature | Company admin |
| `GET` | `/companies/features/subscriptions/{id}/` | Détail feature company | Company membre |
| `PUT` | `/companies/features/subscriptions/{id}/` | Mise à jour abonnement | Company admin |
| `DELETE` | `/companies/features/subscriptions/{id}/` | Se désabonner | Company admin |

#### **Actions Custom**

### **1. Increment Usage** 📈

```python
POST /companies/features/subscriptions/{id}/increment-usage/
```

**Description** : Incrémente l'utilisation d'une feature

**Input** :
```json
{
    "amount": 5  // Quantité à ajouter (default: 1)
}
```

**Validations** :
- `amount` doit être positif
- Vérification limite avant incrément

**Output Succès** :
```json
{
    "message": "Utilisation incrémentée de 5",
    "current_usage": 45,
    "usage_limit": 100,
    "usage_percentage": 45.0,
    "limit_reached": false
}
```

**Output Erreur Limite** :
```json
{
    "error": "Limite d'utilisation atteinte (100)"
}
```

### **2. Reset Usage** 🔄

```python
POST /companies/features/subscriptions/{id}/reset-usage/
```

**Description** : Remet à zéro l'utilisation d'une feature

**Output** :
```json
{
    "message": "Utilisation remise à zéro",
    "old_usage": 45,
    "current_usage": 0
}
```

### **3. Toggle Enabled** 🔄

```python
POST /companies/features/subscriptions/{id}/toggle-enabled/
```

**Description** : Active/désactive une feature pour une entreprise

**Output** :
```json
{
    "message": "Feature activée",
    "is_enabled": true,
    "is_active": true
}
```

### **4. By Company** 🏢

```python
GET /companies/features/subscriptions/by-company/?company_id=123
```

**Description** : Features groupées par entreprise

**Query Params** :
- `company_id` (required) : ID de l'entreprise

**Output** :
```json
{
    "company_id": 123,
    "features_by_type": {
        "websites": [
            {
                "id": 1,
                "feature_name": "Sites Web",
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
                "id": 2,
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

### **5. Usage Stats** 📊

```python
GET /companies/features/subscriptions/usage-stats/
```

**Description** : Statistiques d'utilisation des features

**Output** :
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

### **6. Companies Overview** 🏢📊

```python
GET /companies/features/subscriptions/companies-overview/
```

**Description** : Vue d'ensemble des features par entreprise (superuser seulement)

**Output** :
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

## 🔐 Permissions & Sécurité

### **Niveaux d'Accès Features**

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

### **Restrictions Admin Features**

```python
def perform_create(self, serializer):
    """Création (admin seulement)"""
    if not self.request.user.is_superuser:
        raise PermissionError("Seuls les administrateurs peuvent créer des features")
```

## 🔧 Configuration & Filtres

### **Filtres CompanyFeature**

```python
filterset_fields = ['company', 'feature', 'is_enabled']
search_fields = ['company__name', 'feature__display_name']
ordering_fields = ['created_at', 'expires_at']
ordering = ['-created_at']
```

### **Optimisations Queryset**

```python
queryset = CompanyFeature.objects.select_related('company', 'feature').all()
```

Ce système permet une **gestion flexible des abonnements features** avec **tracking d'usage précis** et **analytics avancées** pour optimiser l'engagement des entreprises sur MEGAHUB.