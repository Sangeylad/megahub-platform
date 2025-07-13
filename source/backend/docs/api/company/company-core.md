# Company Core - Documentation Complète

## 🎯 Objectif de l'App

**company_core** est l'app centrale de gestion des entreprises dans MEGAHUB. Elle fournit le modèle `Company` principal avec trial system, business mode detection, et intégration billing.

## 📁 Structure de l'App

```
company_core/
├── models/
│   └── company.py          # Modèle Company principal
├── serializers/
│   └── company_serializers.py  # Serializers CRUD
├── views/
│   └── company_views.py    # ViewSet avec actions custom
└── urls.py                 # Routes REST
```

## 🏗️ Modèles de Données

### **Company** - Modèle Principal

```python
class Company(TimestampedMixin, SoftDeleteMixin):
    """Modèle Company de base - Entité principale de facturation"""
```

#### **Champs Principaux**

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `name` | CharField(255) | Nom de l'entreprise cliente | Required |
| `admin` | OneToOneField(CustomUser) | Administrateur principal | CASCADE, required |
| `billing_email` | EmailField | Email de facturation | Required |
| `description` | TextField | Description libre | Optional |
| `url` | URLField(255) | Site web entreprise | Default: 'http://example.com' |
| `is_active` | BooleanField | Entreprise active | Default: True |
| `stripe_customer_id` | CharField(255) | ID client Stripe | Optional |

#### **Trial System** 🆕

| Champ | Type | Description | Utilisation |
|-------|------|-------------|-------------|
| `trial_expires_at` | DateTimeField | Date expiration trial | Null = pas de trial |

#### **Indexes Optimisés**

```python
indexes = [
    models.Index(fields=['is_active']),
    models.Index(fields=['stripe_customer_id']),
    models.Index(fields=['trial_expires_at']),  # 🆕 Trial
]
```

### **Relations avec Autres Apps**

```python
# Relations inverses automatiques
company.brands          # brands_core.Brand.filter(company=company)
company.members          # users_core.CustomUser.filter(company=company)
company.slots            # company_slots.CompanySlots (OneToOne)
company.subscription     # billing_core.Subscription (OneToOne)
company.company_features # company_features.CompanyFeature.filter(company=company)
```

## 🔧 Méthodes Business

### **Validation Slots**

```python
def can_add_brand(self):
    """Vérifie si l'entreprise peut ajouter une brand"""
    try:
        slots = self.slots
        return slots.current_brands_count < slots.brands_slots
    except CompanySlots.DoesNotExist:
        return False

def can_add_user(self):
    """Vérifie si l'entreprise peut ajouter un utilisateur"""
    try:
        slots = self.slots
        return slots.current_users_count < slots.users_slots
    except CompanySlots.DoesNotExist:
        return False
```

### **Trial Management** 🆕

```python
def is_in_trial(self):
    """Vérifie si la company est en période d'essai"""
    if not self.trial_expires_at:
        return False
    return timezone.now() <= self.trial_expires_at

def trial_days_remaining(self):
    """Nombre de jours restants dans le trial"""
    if not self.is_in_trial():
        return 0
    remaining = self.trial_expires_at - timezone.now()
    return remaining.days
```

### **Business Mode Detection** 🆕

```python
def is_solo_business(self):
    """Détecte si c'est un business solo (1 brand exactement)"""
    return self.brands.filter(is_deleted=False).count() == 1

def is_agency(self):
    """Détecte si c'est une agence (2+ brands)"""
    return self.brands.filter(is_deleted=False).count() >= 2

def get_business_mode(self):
    """Retourne le mode business actuel"""
    if self.is_solo_business():
        return 'solo'      # Business solo
    elif self.is_agency():
        return 'agency'    # Agence multi-brands
    else:
        return 'empty'     # Aucune brand active
```

#### **Business Modes** - Choix Disponibles

| Mode | Condition | Description |
|------|-----------|-------------|
| `'solo'` | 1 brand exactement | Business solo, modèle classique |
| `'agency'` | 2+ brands | Agence, modèle multi-clients |
| `'empty'` | 0 brands actives | Company vide, en setup |

### **Enhanced Stats** 🆕

```python
def get_stats_summary(self):
    """Résumé des statistiques company"""
    try:
        slots = self.slots
        brands_count = self.brands.filter(is_deleted=False).count()
        users_count = self.members.filter(is_active=True).count()
        
        return {
            'business_mode': self.get_business_mode(),
            'is_in_trial': self.is_in_trial(),
            'trial_days_remaining': self.trial_days_remaining(),
            'brands': {
                'current': brands_count,
                'limit': slots.brands_slots,
                'can_add': self.can_add_brand()
            },
            'users': {
                'current': users_count,
                'limit': slots.users_slots,
                'can_add': self.can_add_user()
            }
        }
    except CompanySlots.DoesNotExist:
        return {
            'business_mode': self.get_business_mode(),
            'is_in_trial': self.is_in_trial(),
            'trial_days_remaining': self.trial_days_remaining(),
            'error': 'CompanySlots not found'
        }
```

## 📝 Serializers

### **CompanySerializer** - Serializer Principal

```python
class CompanySerializer(StatsMixin, RelatedFieldsMixin, serializers.ModelSerializer):
    """Serializer pour Company avec champs calculés"""
```

#### **Champs Standard**

```python
fields = [
    'id', 'name', 'admin', 'billing_email', 'description', 'url',
    'is_active', 'stripe_customer_id', 'created_at', 'updated_at',
    # Champs calculés
    'can_add_brand', 'can_add_user', 'brands_count', 'users_count',
    # Champs relationnels
    'admin_details', 'slots_info', 'subscription_info'
]

read_only_fields = ['stripe_customer_id', 'created_at', 'updated_at']
```

#### **Champs Calculés**

| Champ | Type | Description | Méthode |
|-------|------|-------------|---------|
| `can_add_brand` | Boolean | Peut ajouter brand | `obj.can_add_brand()` |
| `can_add_user` | Boolean | Peut ajouter user | `obj.can_add_user()` |
| `brands_count` | Integer | Nombre brands actives | `obj.brands.filter(is_deleted=False).count()` |
| `users_count` | Integer | Nombre users actifs | `obj.members.filter(is_active=True).count()` |

#### **Admin comme Objet** ✅ CORRECTION

```python
def get_admin(self, obj):
    """Retourne les infos de l'admin au lieu de juste l'ID"""
    if obj.admin:
        return {
            'id': obj.admin.id,
            'username': obj.admin.username,
            'email': obj.admin.email,
            'first_name': obj.admin.first_name,
            'last_name': obj.admin.last_name,
        }
    return None
```

#### **Champs Relationnels Optionnels** (context-based)

```python
# Usage: context={'expand': ['admin_details', 'slots_info']}

def get_admin_details(self, obj):
    """Détails de l'admin (si expand=admin_details)"""
    
def get_slots_info(self, obj):
    """Informations sur les slots (si expand=slots_info)"""
    return {
        'brands_slots': slots.brands_slots,
        'users_slots': slots.users_slots,
        'current_brands_count': slots.current_brands_count,
        'current_users_count': slots.current_users_count,
        'brands_usage_percentage': slots.get_brands_usage_percentage(),
        'users_usage_percentage': slots.get_users_usage_percentage(),
    }

def get_subscription_info(self, obj):
    """Informations sur l'abonnement (si expand=subscription_info)"""
    return {
        'id': subscription.id,
        'plan_name': subscription.plan.display_name,
        'status': subscription.get_status_display(),
        'current_period_end': subscription.current_period_end,
        'amount': subscription.amount,
        'is_active': subscription.is_active(),
        'days_until_renewal': subscription.days_until_renewal(),
    }
```

### **CompanyListSerializer** - Vue Liste Allégée

```python
fields = [
    'id', 'name', 'billing_email', 'admin_username', 'is_active', 'created_at',
    'brands_count', 'users_count', 'plan_name'
]
```

### **CompanyCreateSerializer** - Création avec Admin

```python
class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'entreprise avec admin intégré"""
```

#### **Champs de Création**

```python
# Champs company
fields = ['name', 'billing_email', 'description', 'url']

# Champs admin (write_only)
admin_username = CharField(write_only=True)
admin_email = EmailField(write_only=True)
admin_password = CharField(write_only=True, min_length=8)
admin_first_name = CharField(write_only=True, required=False)
admin_last_name = CharField(write_only=True, required=False)
```

#### **Logique de Création Transactionnelle**

```python
def create(self, validated_data):
    """Crée l'entreprise et son admin en transaction atomique"""
    
    # Extraire données admin
    admin_data = {
        'username': validated_data.pop('admin_username'),
        'email': validated_data.pop('admin_email'),
        'password': validated_data.pop('admin_password'),
        'first_name': validated_data.pop('admin_first_name', ''),
        'last_name': validated_data.pop('admin_last_name', ''),
        'user_type': 'agency_admin',
    }
    
    with transaction.atomic():
        # 1. Créer l'utilisateur admin
        admin_user = CustomUser.objects.create_user(**admin_data)
        
        # 2. Créer l'entreprise
        company = Company.objects.create(admin=admin_user, **validated_data)
        
        # 3. Associer l'admin à l'entreprise
        admin_user.company = company
        admin_user.save()
        
        # 4. Créer les slots par défaut
        CompanySlots.objects.create(company=company)
        
        return company
```

#### **Validations Unicité**

```python
def validate_admin_username(self, value):
    """Valide l'unicité du nom d'utilisateur admin"""
    if CustomUser.objects.filter(username=value).exists():
        raise ValidationError("Ce nom d'utilisateur existe déjà")
    return value

def validate_admin_email(self, value):
    """Valide l'unicité de l'email admin"""
    if CustomUser.objects.filter(email=value).exists():
        raise ValidationError("Cette adresse email existe déjà")
    return value
```

### **CompanyUpdateSerializer** - Mise à Jour Simple

```python
fields = ['name', 'billing_email', 'description', 'url', 'is_active']
```

## 🌐 API Endpoints

### **CompanyViewSet** - Routes REST

```python
# URL Base: /companies/
router.register(r'', CompanyViewSet, basename='company')
```

#### **Endpoints Standard**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| `GET` | `/companies/` | Liste companies | Filtrée par user |
| `POST` | `/companies/` | Créer company | Superuser seulement |
| `GET` | `/companies/{id}/` | Détail company | Owner ou superuser |
| `PUT` | `/companies/{id}/` | Mise à jour company | Owner ou superuser |
| `PATCH` | `/companies/{id}/` | Mise à jour partielle | Owner ou superuser |
| `DELETE` | `/companies/{id}/` | Suppression (soft) | Owner ou superuser |

#### **Actions Custom**

### **1. Check Limits** 📊

```python
POST /companies/{id}/check_limits/
```

**Description** : Vérifie les limites d'utilisation et génère des alertes

**Input** : Aucun body requis

**Output** :
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

**Types d'Alertes** :
- `brands_limit` : Limite brands atteinte
- `users_limit` : Limite users atteinte

### **2. Usage Stats** 📈

```python
GET /companies/{id}/usage_stats/
```

**Description** : Statistiques d'utilisation détaillées

**Output** :
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

### **3. Upgrade Slots** 💰

```python
POST /companies/{id}/upgrade_slots/
```

**Description** : Augmente les slots d'une entreprise

**Input** :
```json
{
    "brands_slots": 10,  // Nouveau nombre de slots brands
    "users_slots": 20    // Nouveau nombre de slots users
}
```

**Validations** :
- Au moins `brands_slots` ou `users_slots` requis
- Nouveau nombre ≥ usage actuel
- Validation automatique des slots existants

**Output Succès** :
```json
{
    "message": "Slots mis à jour avec succès",
    "brands_slots": 10,
    "users_slots": 20,
    "brands_available": 7,
    "users_available": 13
}
```

**Output Erreur** :
```json
{
    "error": "Impossible de réduire à 3 slots, 5 brands utilisées"
}
```

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
        return queryset.filter(id=user.company_id)
    
    # Autres utilisateurs ne voient que leur entreprise
    if user.company:
        return queryset.filter(id=user.company_id)
    
    return queryset.none()
```

### **Restrictions de Création**

```python
def perform_create(self, serializer):
    """Création (superuser seulement)"""
    if not self.request.user.is_superuser:
        raise PermissionDenied("Seuls les administrateurs peuvent créer des entreprises")
    return super().perform_create(serializer)
```

### **Suppression Logique**

```python
def perform_destroy(self, instance):
    """Suppression logique via is_active=False"""
    instance.is_active = False
    instance.save()
```

## 🔧 Configuration & Filtres

### **Filtres Disponibles**

```python
filterset_fields = ['is_active', 'admin']
search_fields = ['name', 'billing_email', 'admin__username']
ordering_fields = ['name', 'created_at', 'updated_at']
ordering = ['-created_at']  # Plus récentes en premier
```

### **Optimisations Queryset**

```python
queryset = Company.objects.select_related('admin').prefetch_related(
    'brands', 'members', 'slots'
)
```

Cette configuration garantit des **performances optimales** et une **sécurité stricte** pour la gestion des entreprises dans MEGAHUB.