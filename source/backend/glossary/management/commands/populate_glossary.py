# backend/glossary/management/commands/populate_glossary.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from glossary.models import TermCategory, Term, TermTranslation, TermRelation


class Command(BaseCommand):
    help = 'Peuple le glossaire avec un dataset business complet'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Supprime toutes les données existantes')
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans écriture')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reset = options['reset']
        
        if reset and not dry_run:
            self.stdout.write('🗑️  Suppression des données existantes...')
            TermTranslation.objects.all().delete()
            TermRelation.objects.all().delete()
            Term.objects.all().delete()
            TermCategory.objects.all().delete()
        
        stats = {
            'categories': 0,
            'terms': 0,
            'translations': 0,
            'relations': 0
        }
        
        try:
            with transaction.atomic():
                self.create_categories(stats, dry_run)
                self.create_terms(stats, dry_run)
                self.create_relations(stats, dry_run)
                
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING('\n🔄 DRY RUN - Aucune donnée sauvegardée'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {str(e)}'))
            return
        
        # Rapport final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RAPPORT DE CRÉATION'))
        self.stdout.write(f'📁 Catégories créées: {stats["categories"]}')
        self.stdout.write(f'📝 Termes créés: {stats["terms"]}')
        self.stdout.write(f'🌍 Traductions créées: {stats["translations"]}')
        self.stdout.write(f'🔗 Relations créées: {stats["relations"]}')
        self.stdout.write('\n✅ Import terminé avec succès!')

    def create_categories(self, stats, dry_run):
        """Crée la structure des catégories"""
        
        categories_data = [
            # Marketing Digital
            {
                'name': 'Marketing Digital',
                'description': 'Stratégies, outils et techniques du marketing numérique moderne',
                'color': '#FF6B6B',
                'icon': 'fas fa-bullhorn',
                'children': [
                    {
                        'name': 'SEO & Contenu',
                        'description': 'Optimisation pour moteurs de recherche et création de contenu',
                        'color': '#4ECDC4',
                        'icon': 'fas fa-search'
                    },
                    {
                        'name': 'Publicité Payante',
                        'description': 'Google Ads, Facebook Ads, programmatique et acquisition payante',
                        'color': '#45B7D1',
                        'icon': 'fas fa-ad'
                    },
                    {
                        'name': 'Marketing Automation',
                        'description': 'Automatisation, email marketing et nurturing de leads',
                        'color': '#96CEB4',
                        'icon': 'fas fa-robot'
                    },
                    {
                        'name': 'Analytics & Data',
                        'description': 'Mesure de performance et analyse de données marketing',
                        'color': '#FECA57',
                        'icon': 'fas fa-chart-line'
                    }
                ]
            },
            
            # Sales
            {
                'name': 'Sales',
                'description': 'Processus commercial, négociation et gestion de la relation client',
                'color': '#FF9F43',
                'icon': 'fas fa-handshake',
                'children': [
                    {
                        'name': 'Prospection',
                        'description': 'Identification et qualification des prospects',
                        'color': '#F8B500',
                        'icon': 'fas fa-crosshairs'
                    },
                    {
                        'name': 'Négociation & Closing',
                        'description': 'Techniques de négociation et finalisation des ventes',
                        'color': '#E55039',
                        'icon': 'fas fa-pen-nib'
                    },
                    {
                        'name': 'CRM & Pipeline',
                        'description': 'Gestion de la relation client et suivi du pipeline commercial',
                        'color': '#3C6382',
                        'icon': 'fas fa-funnel-dollar'
                    }
                ]
            },
            
            # Business & Strategy
            {
                'name': 'Business & Strategy',
                'description': 'Stratégie d\'entreprise, finance et management',
                'color': '#6C5CE7',
                'icon': 'fas fa-chess',
                'children': [
                    {
                        'name': 'Analyse Financière',
                        'description': 'Métriques financières et indicateurs de performance',
                        'color': '#A29BFE',
                        'icon': 'fas fa-calculator'
                    },
                    {
                        'name': 'Stratégie d\'Entreprise',
                        'description': 'Planification stratégique et développement business',
                        'color': '#74B9FF',
                        'icon': 'fas fa-compass'
                    },
                    {
                        'name': 'Management & Leadership',
                        'description': 'Gestion d\'équipe et leadership organisationnel',
                        'color': '#00B894',
                        'icon': 'fas fa-users'
                    }
                ]
            },
            
            # Tech & Data
            {
                'name': 'Tech & Data',
                'description': 'Technologies, développement et gestion des données',
                'color': '#2D3436',
                'icon': 'fas fa-code',
                'children': [
                    {
                        'name': 'Développement Web',
                        'description': 'Technologies web, frameworks et bonnes pratiques',
                        'color': '#636E72',
                        'icon': 'fas fa-laptop-code'
                    },
                    {
                        'name': 'Data Science & BI',
                        'description': 'Science des données et intelligence business',
                        'color': '#00CEC9',
                        'icon': 'fas fa-database'
                    }
                ]
            }
        ]
        
        for cat_data in categories_data:
            parent = self.create_category(cat_data, None, stats, dry_run)
            
            for child_data in cat_data.get('children', []):
                self.create_category(child_data, parent, stats, dry_run)

    def create_category(self, data, parent, stats, dry_run):
        """Crée une catégorie individuelle"""
        
        slug = slugify(data['name'])
        
        if not dry_run:
            category, created = TermCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'parent': parent,
                    'color': data['color'],
                    'icon': data['icon'],
                    'is_active': True
                }
            )
        else:
            created = True
            category = None
        
        if created:
            stats['categories'] += 1
            indent = '  ' if parent else ''
            self.stdout.write(f'{indent}📁 {data["name"]}')
        
        return category

    def create_terms(self, stats, dry_run):
        """Crée tous les termes du glossaire"""
        
        terms_data = [
            # Marketing Digital - Base
            {
                'category_path': 'Marketing Digital',
                'slug': 'inbound-marketing',
                'translations': {
                    'fr': {
                        'title': 'Inbound Marketing',
                        'definition': 'Stratégie marketing qui consiste à attirer les clients vers soi plutôt que d\'aller les chercher, via du contenu de qualité et des expériences personnalisées.',
                        'examples': 'Blog SEO, webinaires, ebooks gratuits, newsletters. L\'inbound génère 54% plus de leads que l\'outbound traditionnel.',
                        'formula': 'Inbound = Attirer + Convertir + Conclure + Fidéliser'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': ''
            },
            {
                'category_path': 'Marketing Digital',
                'slug': 'buyer-persona',
                'translations': {
                    'fr': {
                        'title': 'Buyer Persona',
                        'definition': 'Représentation semi-fictive du client idéal basée sur des données réelles et des insights sur les comportements, motivations et objectifs.',
                        'examples': 'Marie, 35 ans, CMO startup, cherche des solutions marketing automation, budget 5-15K€/mois, décide en 2 semaines.',
                        'benchmarks': '71% des entreprises qui dépassent leurs objectifs de leads utilisent des personas documentés'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner'
            },
            
            # SEO & Contenu
            {
                'category_path': 'Marketing Digital > SEO & Contenu',
                'slug': 'seo',
                'translations': {
                    'fr': {
                        'title': 'SEO',
                        'definition': 'Search Engine Optimization - Ensemble de techniques visant à optimiser la visibilité d\'un site web dans les résultats naturels des moteurs de recherche.',
                        'examples': 'Optimiser les balises title, créer du contenu de qualité, obtenir des backlinks. Le SEO génère 1000%+ de trafic en plus que les réseaux sociaux.',
                        'formula': 'SEO = Technique + Contenu + Popularité (backlinks)'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'seo'
            },
            {
                'category_path': 'Marketing Digital > SEO & Contenu',
                'slug': 'beroas',
                'translations': {
                    'fr': {
                        'title': 'BEROAS',
                        'definition': 'Méthode d\'évaluation de la performance SEO : Bounce rate, Engagement, Reach, Objectives, Actions, Success. Framework pour mesurer l\'efficacité globale d\'une stratégie SEO.',
                        'examples': 'Site e-commerce : Bounce 35%, Engagement 4min, Reach 50K/mois, Objectifs atteints 80%, Actions optimisées, Success = BEROAS 8.5/10',
                        'formula': 'BEROAS = (Bounce + Engagement + Reach + Objectives + Actions + Success) / 6'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'seo'
            },
            {
                'category_path': 'Marketing Digital > SEO & Contenu',
                'slug': 'serp',
                'translations': {
                    'fr': {
                        'title': 'SERP',
                        'definition': 'Search Engine Results Page - Page de résultats affichée par un moteur de recherche en réponse à une requête utilisateur.',
                        'examples': 'SERP pour "chaussures running" : 10 liens naturels + 4 annonces + images + avis + questions fréquentes.',
                        'benchmarks': 'Position 1 : 28.5% de clics, Position 2 : 15.7%, Position 10 : 2.5%'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'seo'
            },
            {
                'category_path': 'Marketing Digital > SEO & Contenu',
                'slug': 'backlink',
                'translations': {
                    'fr': {
                        'title': 'Backlink',
                        'definition': 'Lien entrant pointant vers votre site depuis un autre site web. Facteur de ranking majeur qui transmet de l\'autorité et du trafic référent.',
                        'examples': 'Un article de TechCrunch qui cite votre startup avec un lien = backlink DR90. Objectif : 50+ backlinks qualité/mois.',
                        'benchmarks': 'Sites top 10 Google ont en moyenne 3.8x plus de backlinks que les positions 11-20'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'seo'
            },
            
            # Publicité Payante
            {
                'category_path': 'Marketing Digital > Publicité Payante',
                'slug': 'cpc',
                'translations': {
                    'fr': {
                        'title': 'CPC',
                        'definition': 'Coût Par Clic - Montant payé par un annonceur chaque fois qu\'un utilisateur clique sur sa publicité.',
                        'examples': 'CPC Google Ads "assurance auto" : 15€, "chaussures" : 1.20€. Budget 1000€ avec CPC 2€ = 500 clics maximum.',
                        'formula': 'CPC = Budget Total / Nombre de Clics'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'ads'
            },
            {
                'category_path': 'Marketing Digital > Publicité Payante',
                'slug': 'cpm',
                'translations': {
                    'fr': {
                        'title': 'CPM',
                        'definition': 'Coût Pour Mille impressions - Prix payé pour 1000 affichages d\'une publicité, indépendamment des clics.',
                        'examples': 'CPM Facebook : 5-15€, LinkedIn : 8-25€, YouTube : 3-8€. Idéal pour campagnes de notoriété avec audience large.',
                        'formula': 'CPM = (Budget Campagne / Impressions) × 1000'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'ads'
            },
            {
                'category_path': 'Marketing Digital > Publicité Payante',
                'slug': 'roas',
                'translations': {
                    'fr': {
                        'title': 'ROAS',
                        'definition': 'Return On Ad Spend - Retour sur investissement publicitaire. Mesure le chiffre d\'affaires généré pour chaque euro dépensé en publicité.',
                        'examples': 'ROAS 4:1 = 4€ de CA pour 1€ de pub. E-commerce rentable : ROAS > 4, SaaS B2B : ROAS > 6.',
                        'formula': 'ROAS = Chiffre d\'Affaires Publicitaire / Coût Publicitaire'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'ads'
            },
            
            # Sales - Prospection
            {
                'category_path': 'Sales > Prospection',
                'slug': 'prospect',
                'translations': {
                    'fr': {
                        'title': 'Prospect',
                        'definition': 'Contact commercial qualifié qui présente un potentiel d\'achat identifié, avec un besoin, un budget et un timing définis.',
                        'examples': 'Prospect qualifié BANT : Besoin confirmé, Autorité de décision, Budget validé 10-50K€, Timing 3 mois.',
                        'benchmarks': 'Taux de conversion lead → prospect : 20-30%, prospect → client : 15-25%'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'sales'
            },
            {
                'category_path': 'Marketing Digital',
                'slug': 'lead',
                'translations': {
                    'fr': {
                        'title': 'Lead',
                        'definition': 'Contact commercial généré par le marketing, ayant manifesté un intérêt mais non encore qualifié par l\'équipe commerciale.',
                        'examples': 'Lead : télécharge un ebook, s\'inscrit à un webinaire. 1000 leads/mois → 200 prospects qualifiés → 30 clients.',
                        'benchmarks': 'Coût moyen lead B2B : 35€, conversion lead-to-customer : 2-5%'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'marketing'
            },
            {
                'category_path': 'Sales > Prospection',
                'slug': 'qualification-bant',
                'translations': {
                    'fr': {
                        'title': 'Qualification BANT',
                        'definition': 'Méthode de qualification des prospects : Budget, Authority (autorité), Need (besoin), Timeline (délai). Framework pour prioriser les opportunités commerciales.',
                        'examples': 'Budget 50K€ ✓, DG décideur ✓, Besoin CRM confirmé ✓, Timeline 6 mois ✓ = Prospect hautement qualifié.',
                        'benchmarks': 'Prospects qualifiés BANT : taux de closing 40-60% vs 5-15% sans qualification'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'sales'
            },
            
            # CRM & Pipeline
            {
                'category_path': 'Sales > CRM & Pipeline',
                'slug': 'pipeline-commercial',
                'translations': {
                    'fr': {
                        'title': 'Pipeline Commercial',
                        'definition': 'Représentation visuelle du processus de vente montrant toutes les opportunités commerciales à différents stades d\'avancement.',
                        'examples': 'Pipeline SaaS : Prospection (100 opps) → Qualification (40) → Démo (20) → Négociation (10) → Signature (5)',
                        'formula': 'Prévision CA = Σ(Valeur Opportunité × Probabilité de Closing)'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'sales'
            },
            {
                'category_path': 'Sales > CRM & Pipeline',
                'slug': 'taux-conversion',
                'translations': {
                    'fr': {
                        'title': 'Taux de Conversion',
                        'definition': 'Pourcentage de prospects qui passent d\'une étape à l\'autre dans le processus de vente, ou qui deviennent clients.',
                        'examples': 'Lead → Prospect : 25%, Prospect → Opportunity : 40%, Opportunity → Client : 20%. Taux global : 2%.',
                        'benchmarks': 'SaaS B2B moyen : 15-20%, E-commerce : 2-3%, Services haut de gamme : 5-10%'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'sales'
            },
            
            # Business & Strategy
            {
                'category_path': 'Business & Strategy > Analyse Financière',
                'slug': 'ltv',
                'translations': {
                    'fr': {
                        'title': 'LTV',
                        'definition': 'Lifetime Value - Valeur totale qu\'un client apporte à l\'entreprise sur toute la durée de sa relation commerciale.',
                        'examples': 'SaaS 100€/mois, rétention 24 mois : LTV = 2400€. E-commerce : panier moyen 80€ × 5 achats/an × 3 ans = 1200€.',
                        'formula': 'LTV = (Panier Moyen × Fréquence d\'Achat × Durée de Vie Client) - Coûts'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'finance'
            },
            {
                'category_path': 'Business & Strategy > Analyse Financière',
                'slug': 'cac',
                'translations': {
                    'fr': {
                        'title': 'CAC',
                        'definition': 'Customer Acquisition Cost - Coût total pour acquérir un nouveau client, incluant marketing, sales et ressources dédiées.',
                        'examples': 'Budget marketing 50K€/mois, 100 nouveaux clients : CAC = 500€. Objectif : LTV/CAC > 3:1.',
                        'formula': 'CAC = (Coûts Marketing + Coûts Sales) / Nombre de Nouveaux Clients'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'finance'
            },
            {
                'category_path': 'Business & Strategy > Analyse Financière',
                'slug': 'mrr',
                'translations': {
                    'fr': {
                        'title': 'MRR',
                        'definition': 'Monthly Recurring Revenue - Revenus récurrents mensuels prévisibles, métrique clé pour les business models par abonnement.',
                        'examples': '500 clients × 99€/mois = 49 500€ MRR. Croissance MRR : +15% m/m = 57K€ le mois suivant.',
                        'formula': 'MRR = Nombre d\'Abonnés Actifs × Prix Moyen Mensuel'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'saas'
            },
            {
                'category_path': 'Business & Strategy > Analyse Financière',
                'slug': 'churn-rate',
                'translations': {
                    'fr': {
                        'title': 'Churn Rate',
                        'definition': 'Taux d\'attrition - Pourcentage de clients qui cessent d\'utiliser un produit ou service sur une période donnée.',
                        'examples': '1000 clients début mois, 50 résiliations : Churn = 5%. SaaS excellent < 2%/mois, acceptable < 5%/mois.',
                        'formula': 'Churn Rate = (Clients Perdus / Clients Début Période) × 100'
                    }
                },
                'is_essential': True,
                'difficulty': 'intermediate',
                'context': 'saas'
            },
            
            # Tech & Data
            {
                'category_path': 'Tech & Data > Data Science & BI',
                'slug': 'kpi',
                'translations': {
                    'fr': {
                        'title': 'KPI',
                        'definition': 'Key Performance Indicator - Indicateur clé de performance permettant de mesurer l\'atteinte des objectifs stratégiques d\'une organisation.',
                        'examples': 'KPI Marketing : CAC, LTV, taux conversion. KPI Sales : pipeline value, win rate. KPI Produit : DAU, rétention.',
                        'benchmarks': 'Règle : 5-7 KPI max par équipe, mesure mensuelle, objectifs SMART'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'analytics'
            },
            {
                'category_path': 'Tech & Data > Data Science & BI',
                'slug': 'dashboard',
                'translations': {
                    'fr': {
                        'title': 'Dashboard',
                        'definition': 'Tableau de bord visuel qui agrège et présente les métriques et KPI essentiels d\'une activité en temps réel ou quasi-réel.',
                        'examples': 'Dashboard CEO : MRR, Churn, CAC/LTV, Cash. Dashboard Marketing : Leads, CPL, ROAS, Traffic. Mise à jour temps réel.',
                        'benchmarks': '73% des dirigeants consultent leurs dashboards quotidiennement'
                    }
                },
                'is_essential': True,
                'difficulty': 'beginner',
                'context': 'bi'
            }
        ]
        
        for term_data in terms_data:
            self.create_term(term_data, stats, dry_run)

    def create_term(self, data, stats, dry_run):
        """Crée un terme individuel avec ses traductions"""
        
        # Récupérer la catégorie
        category_path_parts = data['category_path'].split(' > ')
        category_slug = slugify(category_path_parts[-1])
        
        if not dry_run:
            try:
                category = TermCategory.objects.get(slug=category_slug)
            except TermCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Catégorie non trouvée: {category_slug}'))
                return
        else:
            category = None
        
        # Créer le terme
        if not dry_run:
            term, created = Term.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'category': category,
                    'is_essential': data.get('is_essential', False),
                    'difficulty_level': data.get('difficulty', 'intermediate'),
                    'is_active': True
                }
            )
        else:
            created = True
            term = None
        
        if created:
            stats['terms'] += 1
            self.stdout.write(f'  📝 {data["translations"]["fr"]["title"]}')
            
            # Créer les traductions
            for lang, translation_data in data['translations'].items():
                if not dry_run:
                    TermTranslation.objects.get_or_create(
                        term=term,
                        language=lang,
                        context=data.get('context', ''),
                        defaults={
                            'title': translation_data['title'],
                            'definition': translation_data['definition'],
                            'examples': translation_data.get('examples', ''),
                            'formula': translation_data.get('formula', ''),
                            'benchmarks': translation_data.get('benchmarks', ''),
                            'sources': translation_data.get('sources', ''),
                        }
                    )
                
                stats['translations'] += 1

    def create_relations(self, stats, dry_run):
        """Crée les relations entre termes"""
        
        relations_data = [
            # Relations SEO
            ('seo', 'beroas', 'related'),
            ('seo', 'serp', 'child'),
            ('seo', 'backlink', 'child'),
            
            # Relations Marketing/Sales
            ('lead', 'prospect', 'child'),
            ('prospect', 'qualification-bant', 'related'),
            ('prospect', 'pipeline-commercial', 'related'),
            
            # Relations Métriques Business
            ('ltv', 'cac', 'related'),
            ('mrr', 'churn-rate', 'related'),
            ('cac', 'roas', 'related'),
            
            # Relations Publicité
            ('cpc', 'cpm', 'related'),
            ('cpc', 'roas', 'related'),
            ('roas', 'ltv', 'related'),
        ]
        
        if not dry_run:
            for from_slug, to_slug, relation_type in relations_data:
                try:
                    from_term = Term.objects.get(slug=from_slug)
                    to_term = Term.objects.get(slug=to_slug)
                    
                    TermRelation.objects.get_or_create(
                        from_term=from_term,
                        to_term=to_term,
                        relation_type=relation_type,
                        defaults={'weight': 5}
                    )
                    
                    stats['relations'] += 1
                    
                except Term.DoesNotExist:
                    continue
        else:
            stats['relations'] = len(relations_data)
        
        if stats['relations'] > 0:
            self.stdout.write(f'  🔗 {stats["relations"]} relations créées')