# 🔌 AI Providers - Providers & Credentials Sécurisées

## Vue d'Ensemble

L'app `ai_providers` gère tous les **providers IA disponibles**, leurs **credentials sécurisées** et les **quotas par company**. Elle fournit une couche d'abstraction pour gérer multiple providers (OpenAI, Anthropic, Google, etc.) avec chiffrement des clés et gestion centralisée des limites.

### Responsabilité
- **AIProvider** : Providers IA disponibles et leurs capacités
- **AICredentials** : Credentials chiffrées par company
- **AIQuota** : Quotas et limites par company/provider
- **Services** : Chiffrement/déchiffrement, validation, monitoring quotas

### Base URL
```
https://backoffice.humari.fr/ai/providers/
https://backoffice.humari.fr/ai/credentials/
```

---

## 📊 Modèles de Données

### AIProvider
```python
# Providers IA disponibles
- name: str (unique) # "openai", "anthropic", "google"
- display_name: str # "OpenAI", "Anthropic Claude"
- base_url: str # URL API de base

# Capacités
- supports_chat: bool # Chat completions
- supports_assistants: bool # Assistants avancés  
- supports_files: bool # Upload de fichiers
- supports_vision: bool # Analyse d'images

# Configuration
- default_model: str # Modèle par défaut
- available_models: JSON # Liste des modèles disponibles
- rate_limit_rpm: int # Requêtes par minute

# Statut
- is_active: bool # Provider activé
```

### AICredentials
```python
# Credentials sécurisées par company
- company: OneToOne → Company

# Clés chiffrées par provider
- openai_api_key: str (chiffré) # Clé OpenAI
- anthropic_api_key: str (chiffré) # Clé Anthropic
- google_api_key: str (chiffré) # Clé Google

# Fallback
- use_global_fallback: bool # Utiliser clés globales si besoin
```

### AIQuota
```python
# Quotas par company/provider
- company: FK → Company
- provider: FK → AIProvider

# Limites mensuelles
- monthly_token_limit: int # Tokens max par mois
- monthly_cost_limit: Decimal # Budget max mensuel

# Compteurs actuels  
- current_tokens_used: int # Tokens consommés ce mois
- current_cost_used: Decimal # Coût consommé ce mois

# Reset automatique
- last_reset_date: Date # Dernière remise à zéro
```

**Contrainte** : `unique_together = ['company', 'provider']`

---

## 🎯 Endpoints

### AIProvider Management

#### `GET /ai/providers/`
**Liste des providers IA disponibles**

**Réponse** :
```json
[
  {
    "id": 1,
    "name": "openai",
    "display_name": "OpenAI",
    "base_url": "https://api.openai.com",
    "supports_chat": true,
    "supports_assistants": true,
    "supports_files": true,
    "supports_vision": true,
    "default_model": "gpt-4o",
    "available_models": [
      "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
    ],
    "rate_limit_rpm": 10000,
    "is_active": true
  },
  {
    "id": 2,
    "name": "anthropic",
    "display_name": "Anthropic Claude",
    "base_url": "https://api.anthropic.com",
    "supports_chat": true,
    "supports_assistants": false,
    "supports_files": false,
    "supports_vision": true,
    "default_model": "claude-3-5-sonnet-20241022",
    "available_models": [
      "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"
    ],
    "rate_limit_rpm": 1000,
    "is_active": true
  }
]
```

#### `GET /ai/providers/{id}/`
**Détail d'un provider spécifique**

### AICredentials Management

#### `GET /ai/credentials/`
**Credentials de la company courante**

**Filtrage automatique** : Par `request.user.company`

**Réponse** :
```json
[
  {
    "id": 1,
    "company": {"id": 1, "name": "Humari"},
    "has_openai_key": true,          // ✅ Jamais la vraie clé
    "has_anthropic_key": false,
    "has_google_key": false,
    "use_global_fallback": false,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-12-20T14:30:00Z"
  }
]
```

**Sécurité** : Les clés réelles ne sont **jamais** exposées, seulement des booléens `has_*_key`.

#### `POST /ai/credentials/`
**Créer/mettre à jour credentials**

**Paramètres** :
```json
{
  "openai_api_key": "sk-proj-abc123...",     // Chiffré automatiquement
  "anthropic_api_key": "",                   // Vide = pas de changement
  "google_api_key": "AIza-def456...",
  "use_global_fallback": false
}
```

**Chiffrement automatique** : Les clés sont chiffrées avec `Fernet` avant stockage.

**Réponse** :
```json
{
  "message": "Credentials updated successfully",
  "has_openai_key": true,
  "has_anthropic_key": false, 
  "has_google_key": true,
  "providers_configured": ["openai", "google"]
}
```

#### `PUT /ai/credentials/{id}/`
**Mise à jour credentials existantes**

#### `DELETE /ai/credentials/{id}/`
**Suppression credentials** (cascade vers quotas)

---

## 🎛️ Actions Spécialisées

### Test de Connexion

#### `POST /ai/credentials/test_connection/`
**Tester la validité d'une clé API**

**Paramètres** :
```json
{
  "provider": "openai"    // Provider à tester
}
```

**Workflow** :
1. Récupère la clé déchiffrée pour le provider
2. Fait un appel API test (minimal cost)
3. Valide la réponse

**Réponse succès** :
```json
{
  "success": true,
  "provider": "openai",
  "message": "Connection to OpenAI successful",
  "model_tested": "gpt-3.5-turbo",
  "response_time_ms": 245
}
```

**Réponse erreur** :
```json
{
  "success": false,
  "provider": "openai", 
  "error": "Invalid API key",
  "error_code": "INVALID_API_KEY"
}
```

### Statut des Quotas

#### `GET /ai/credentials/quota_status/`
**Statut des quotas pour un provider**

**Paramètres** :
- `?provider=openai` (requis)

**Réponse** :
```json
{
  "provider": "openai",
  "company": {"id": 1, "name": "Humari"},
  "quota": {
    "monthly_token_limit": 1000000,
    "monthly_cost_limit": "100.00",
    "current_tokens_used": 245670,
    "current_cost_used": "24.56",
    "tokens_remaining": 754330,
    "cost_remaining": "75.44",
    "usage_percentage": 24.57,
    "is_near_limit": false,
    "is_exceeded": false
  },
  "period": {
    "start_date": "2024-12-01",
    "end_date": "2024-12-31",
    "days_remaining": 11
  },
  "projected": {
    "monthly_tokens": 894580,   // Projection fin mois
    "monthly_cost": "89.45",
    "will_exceed_tokens": false,
    "will_exceed_cost": false
  }
}
```

**Alertes calculées** :
- `is_near_limit` : > 80% du quota
- `is_exceeded` : > 100% du quota

---

## 🔐 Services Internes

### CredentialService

#### `get_credentials_for_company(company)`
**Récupère toutes les credentials déchiffrées**

```python
{
  "openai": "sk-proj-abc123...",
  "anthropic": None,
  "google": "AIza-def456..."
}
```

#### `get_api_key_for_provider(company, provider)`
**Récupère la clé déchiffrée pour un provider**

```python
api_key = credential_service.get_api_key_for_provider(company, "openai")
# Retourne: "sk-proj-abc123..." ou None
```

#### `set_credential_for_company(company, provider, api_key)`
**Chiffre et sauvegarde une clé**

```python
success = credential_service.set_credential_for_company(
    company, "openai", "sk-proj-new-key"
)
# Retourne: True/False
```

#### `validate_provider_connection(company, provider)`
**Valide une connexion provider**

```python
result = credential_service.validate_provider_connection(company, "openai")
# Retourne: {"success": True, "response_time_ms": 245} ou erreur
```

### QuotaService

#### `get_quota_status(company, provider)`
**Statut complet des quotas**

#### `consume_quota(company, provider, tokens, cost)`
**Consomme du quota et vérifie les limites**

```python
can_consume = QuotaService.consume_quota(
    company, "openai", 500, Decimal("0.05")
)
# Retourne: True si quota OK, False si dépassé
```

#### `reset_monthly_quotas(company=None)`
**Reset des quotas mensuels (cron job)**

#### `check_quota_alerts(company)`
**Vérifie et génère des alertes quota**

```python
alerts = QuotaService.check_quota_alerts(company)
# Retourne: [{"type": "quota_warning", "provider": "openai", ...}]
```

---

## 🔒 Sécurité et Chiffrement

### Chiffrement des Clés
```python
# Utilise Fernet (AES 128 + HMAC)
from cryptography.fernet import Fernet

# Clé de chiffrement dans settings
AI_ENCRYPTION_KEY = "base64_encoded_key"

# Chiffrement automatique lors save()
encrypted_key = fernet.encrypt(api_key.encode())
```

### Validation des Clés
```python
# Format validation par provider
OPENAI_KEY_PATTERN = r'^sk-[A-Za-z0-9]{32,}$'
ANTHROPIC_KEY_PATTERN = r'^sk-ant-[A-Za-z0-9\-_]{32,}$'
GOOGLE_KEY_PATTERN = r'^AIza[A-Za-z0-9\-_]{35}$'
```

### Rotation des Clés
```python
# Support rotation manuelle
PUT /ai/credentials/{id}/
{
  "openai_api_key": "sk-proj-new-rotated-key"
}

# Archivage ancienne clé (audit trail)
# TODO: Implémenter backup chiffrées
```

---

## 📊 Monitoring et Quotas

### Quotas par Défaut
```python
DEFAULT_QUOTAS = {
    "openai": {
        "monthly_token_limit": 1000000,    # 1M tokens
        "monthly_cost_limit": 100.00       # $100
    },
    "anthropic": {
        "monthly_token_limit": 500000,     # 500K tokens  
        "monthly_cost_limit": 50.00        # $50
    }
}
```

### Reset Automatique
```python
# Cron job mensuel (task_scheduling)
@periodic_task(cron="0 0 1 * *")  # 1er de chaque mois
def reset_monthly_quotas():
    QuotaService.reset_monthly_quotas()
```

### Alertes Quota
```python
# Seuils d'alerte automatiques
QUOTA_WARNING_THRESHOLDS = {
    "tokens": 0.8,    # 80% tokens
    "cost": 0.8,      # 80% budget
    "critical": 0.95  # 95% critique
}
```

---

## 🔄 Intégrations Cross-App

### Avec ai_core
```python
# Lors création AIJob
credentials = CredentialService.get_api_key_for_provider(company, "openai")
if not credentials:
    raise ValidationError("No OpenAI credentials configured")

# Vérification quota avant job
can_consume = QuotaService.consume_quota(company, "openai", estimated_tokens, estimated_cost)
```

### Avec ai_usage
```python
# Après completion job
QuotaService.consume_quota(company, provider, actual_tokens, actual_cost)

# Trigger alertes si dépassement
alerts = QuotaService.check_quota_alerts(company)
```

### Avec ai_openai
```python
# Extension utilise credentials
openai_key = CredentialService.get_api_key_for_provider(company, "openai")
ai_service = AIService(api_key=openai_key)
```

---

## 🚨 Gestion d'Erreurs

### Erreurs de Credentials
```json
// Clé manquante
{
  "error": "No API key configured for provider 'openai'",
  "error_code": "NO_API_KEY",
  "provider": "openai"
}

// Clé invalide
{
  "error": "Invalid API key for provider 'openai'",
  "error_code": "INVALID_API_KEY",
  "provider": "openai",
  "last_validated": "2024-12-15T10:00:00Z"
}
```

### Erreurs de Quota
```json
// Quota dépassé
{
  "error": "Monthly quota exceeded for provider 'openai'", 
  "error_code": "QUOTA_EXCEEDED",
  "provider": "openai",
  "current_usage": "105.67",
  "limit": "100.00"
}

// Quota warning
{
  "warning": "Approaching quota limit for provider 'openai'",
  "warning_code": "QUOTA_WARNING", 
  "usage_percentage": 87.5,
  "remaining_budget": "12.50"
}
```

---

## 🔧 Maintenance et Administration

### Commandes de Gestion
```bash
# Validation toutes les clés
python manage.py validate_all_credentials

# Reset quotas manuellement
python manage.py reset_quotas --company=1 --provider=openai

# Audit clés expirées
python manage.py audit_expired_keys

# Backup credentials chiffrées
python manage.py backup_credentials --output=/backup/
```

### Health Checks
```python
# Endpoint health providers
GET /ai/providers/health/
{
  "openai": {"status": "healthy", "response_time_ms": 245},
  "anthropic": {"status": "error", "error": "Invalid API key"},
  "google": {"status": "not_configured"}
}
```

### Monitoring Alertes
```python
# Alertes automatiques via ai_usage
- Quota > 80% → Email warning
- Quota > 100% → Email critical + disable jobs
- Clé expirée → Email admin
- Échecs connexion répétés → Email technique
```

---

## 💡 Bonnes Pratiques

### Gestion des Clés
1. **Rotation régulière** (tous les 3 mois)
2. **Principe du moindre privilège** (clés par environnement)
3. **Monitoring des accès** (logs d'utilisation)
4. **Backup sécurisé** des clés chiffrées

### Quotas
1. **Budgets réalistes** selon usage prévu
2. **Alertes préventives** à 80%
3. **Reset automatique** en début de mois
4. **Projection de consommation** pour anticipation

### Sécurité
1. **Chiffrement au repos** avec Fernet
2. **Validation format** avant stockage
3. **Audit trail** des modifications
4. **Isolation par company** stricte

---

**Cette documentation couvre la gestion complète des providers et credentials. Pour l'utilisation concrète avec OpenAI, voir [ai_openai](./openai.md).**