# 🚀 MegaHub Platform

> **Enterprise React 19 + Django Platform with Multi-Environment Architecture**

[![React](https://img.shields.io/badge/React-19.1.0-blue?logo=react)](https://react.dev)
[![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)](https://djangoproject.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-blue?logo=typescript)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-blue?logo=docker)](https://docker.com)

## 🏗️ Architecture Leaders

MegaHub Platform suit les standards des leaders technologiques (Netflix, Stripe, Airbnb) avec :

- **🎯 Multi-Environment Setup** : Development, Staging, Production
- **🚀 React 19** : Server Components, React Compiler, TanStack Router v5
- **🐍 Django Multi-DB** : Architecture modulaire avec 50+ apps
- **🐳 Docker Orchestration** : Multi-stage builds optimisés
- **🔒 Enterprise Security** : SSL/TLS, CSP, Rate limiting
- **📊 Performance First** : Build < 1.2s, Bundle < 350kb

## 📁 Structure

```
megahub-platform/
├── source/                          # 🏠 Code source (jamais écrasé)
│   ├── backend/                     # Django avec 50+ apps modulaires
│   │   ├── django_app/
│   │   ├── settings/                # Multi-environment settings
│   │   ├── ai_core/                 # IA & templates
│   │   ├── seo_pages_content/       # SEO & content
│   │   └── company_core/            # Business logic
│   └── frontend/                    # React 19 + TanStack v5
│       ├── src/                     # TypeScript strict
│       ├── vite.config.ts           # Lightning CSS + React Compiler
│       └── Dockerfile               # Multi-stage optimisé
├── deployments/                     # 🚀 Environnements séparés
│   ├── development/
│   ├── staging/
│   └── production/
├── infrastructure/                  # 🔧 Configs & monitoring
├── scripts/                        # 📋 Déploiement orchestré
│   ├── deploy-env.sh               # Déploiement multi-env
│   └── utils-env.sh                # Utilitaires par env
├── docker-compose.yml              # Development
├── docker-compose.staging.yml      # Staging
└── docker-compose.production.yml   # Production
```

## 🚀 Quick Start

### Development
```bash
# Clone & setup
git clone https://github.com/Sangeylad/megahub-platform.git
cd megahub-platform

# Deploy development environment
./scripts/deploy-env.sh development

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/admin
```

### Staging
```bash
# Deploy to staging
./scripts/deploy-env.sh staging

# Access: https://staging.megahub.humari.fr
```

### Production
```bash
# Deploy to production (confirmation required)
./scripts/deploy-env.sh production

# Access: https://megahub.humari.fr
```

## 🛠️ Development Workflow

### Daily Development
```bash
# Start development
./scripts/utils-env.sh development status
./scripts/utils-env.sh development logs

# Make changes in source/
# Test locally on localhost:3000

# Deploy when ready
./scripts/deploy-env.sh development
```

### Feature Development
```bash
# 1. Develop locally
npm run dev  # Frontend
python manage.py runserver  # Backend

# 2. Test on staging
git push origin develop
./scripts/deploy-env.sh staging

# 3. Deploy to production
git push origin main
./scripts/deploy-env.sh production
```

## 🏆 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Build Time | < 2s | ✅ < 1.2s |
| Bundle Size | Optimized | ✅ 274kb gzipped |
| First Load | < 1s | ✅ < 650ms |
| Lighthouse | > 95 | ✅ 98/100 |
| TypeScript | 0% any | ✅ Strict mode |

## 🔧 Tech Stack

### Frontend
- **React 19.1.0** - Server Components + Actions + Compiler
- **TanStack Router v1.127** - File-based routing + preloading
- **TanStack Query v5.82** - Data fetching + Suspense
- **TypeScript 5.8.3** - Strict mode + inference
- **Vite 6.3.5** - Lightning CSS + build optimizations
- **Tailwind CSS v4** - CSS-first + Oxide engine

### Backend
- **Django 5.0** - Multi-app architecture
- **PostgreSQL 15** - Multi-database setup
- **Redis 7** - Caching + Celery
- **Docker** - Multi-stage production builds

### Infrastructure
- **nginx** - Reverse proxy + SSL termination
- **Let's Encrypt** - Automatic SSL certificates
- **GitHub Actions** - CI/CD pipeline
- **Multi-environment** - Dev/Staging/Production

## 📊 Monitoring & Debugging

```bash
# Environment status
./scripts/utils-env.sh {development|staging|production} status

# Real-time logs
./scripts/utils-env.sh {environment} logs

# Performance testing
curl -w "%{time_total}" https://megahub.humari.fr/

# Health checks
curl -f https://megahub.humari.fr/health
```

## 🚨 Troubleshooting

### Common Issues

**Build fails:**
```bash
# Check TypeScript
npm run type-check:strict

# Clear cache
rm -rf node_modules/ package-lock.json
npm install
```

**Database issues:**
```bash
# Check migrations
python manage.py showmigrations
python manage.py migrate
```

**Docker issues:**
```bash
# Rebuild containers
docker-compose down
docker-compose up -d --build
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat(scope): add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

This project is proprietary software owned by Humari.

## 🔗 Links

- [Frontend Demo](https://megahub.humari.fr)
- [API Documentation](https://backoffice.humari.fr)
- [Staging Environment](https://staging.megahub.humari.fr)

---

**Built with ❤️ by the MegaHub Team**
