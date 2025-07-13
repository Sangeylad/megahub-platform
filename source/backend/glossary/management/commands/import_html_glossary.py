# backend/glossary/management/commands/import_html_glossary.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from glossary.models import TermCategory, Term, TermTranslation, TermRelation
import re


class Command(BaseCommand):
    help = 'Importe les termes depuis l\'ancien glossaire HTML'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans écriture')
        parser.add_argument('--update', action='store_true', help='Met à jour les termes existants')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update']
        
        stats = {
            'categories_created': 0,
            'terms_created': 0,
            'terms_updated': 0,
            'translations_created': 0,
            'relations_created': 0
        }
        
        try:
            with transaction.atomic():
                # Créer les catégories
                self.ensure_categories(stats, dry_run)
                
                # Importer les termes hardcodés
                self.import_hardcoded_terms(stats, dry_run, update_existing)
                
                # Créer les relations
                self.create_relations(stats, dry_run)
                
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING('\n🔄 DRY RUN - Aucune donnée sauvegardée'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {str(e)}'))
            raise
        
        self.print_stats(stats)

    def ensure_categories(self, stats, dry_run):
        """Crée les catégories nécessaires"""
        categories_data = [
            # Parents d'abord
            {'slug': 'marketing-digital', 'name': 'Marketing Digital', 'parent': None, 'color': '#FF6B6B'},
            {'slug': 'ecommerce', 'name': 'E-commerce', 'parent': None, 'color': '#4ECDC4'},
            
            # Enfants
            {'slug': 'publicite-payante', 'name': 'Publicité Payante', 'parent': 'marketing-digital', 'color': '#45B7D1'},
            {'slug': 'beroas', 'name': 'BEROAS & Rentabilité', 'parent': 'ecommerce', 'color': '#667eea'},
            {'slug': 'costs', 'name': 'Coûts & Marges', 'parent': 'ecommerce', 'color': '#96CEB4'},
            {'slug': 'marketing', 'name': 'Marketing & Pub', 'parent': 'marketing-digital', 'color': '#FECA57'},
        ]
        
        for cat_data in categories_data:
            if not dry_run:
                parent = None
                if cat_data['parent']:
                    parent = TermCategory.objects.get(slug=cat_data['parent'])
                
                category, created = TermCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults={
                        'name': cat_data['name'],
                        'parent': parent,
                        'color': cat_data['color'],
                        'is_active': True
                    }
                )
                
                if created:
                    stats['categories_created'] += 1
                    self.stdout.write(f'📁 Catégorie créée: {cat_data["name"]}')

    def import_hardcoded_terms(self, stats, dry_run, update_existing):
        """Importe les termes hardcodés depuis ton HTML"""
        
        terms_data = [
            {
                'slug': 'beroas',
                'category_slug': 'beroas',
                'title': 'BEROAS',
                'definition': 'Budget Efficiency Return On Ad Spend - Indique combien vous pouvez dépenser en publicité pour chaque euro de chiffre d\'affaires tout en restant rentable.',
                'examples': 'BEROAS de 3 = pour 100€ de CA, vous pourrez dépenser au maximum 33€ en publicité tout en conservant votre rentabilité.',
                'formula': 'BEROAS = Prix de vente ÷ Marge unitaire',
                'context': 'ecommerce'
            },
            {
                'slug': 'roas',
                'category_slug': 'marketing',
                'title': 'ROAS',
                'definition': 'Return On Ad Spend - Chiffre d\'affaires généré pour chaque euro investi en publicité. Attention : ne tient pas compte des coûts !',
                'examples': 'ROAS 4:1 = 4€ de CA pour 1€ de pub. E-commerce rentable : ROAS > 4, SaaS B2B : ROAS > 6.',
                'formula': 'ROAS = Chiffre d\'Affaires Publicitaire / Coût Publicitaire',
                'context': 'ads'
            },
            {
                'slug': 'marge',
                'category_slug': 'costs',
                'title': 'Marge Unitaire',
                'definition': 'Bénéfice réalisé sur chaque produit vendu après déduction de tous les coûts.',
                'examples': 'Produit à 30€, coûts totaux 18€ → Marge = 12€',
                'formula': 'Prix de vente - (Coût produit + Frais livraison + Frais bancaires + Autres coûts)',
                'context': 'finance'
            },
            {
                'slug': 'taux-marge',
                'category_slug': 'costs',
                'title': 'Taux de Marge',
                'definition': 'Pourcentage de bénéfice par rapport au prix de vente.',
                'examples': '',
                'formula': '(Marge unitaire ÷ Prix de vente) × 100',
                'benchmarks': 'Minimum viable 20%, Idéal 40%+, Excellent 60%+',
                'context': 'finance'
            },
            {
                'slug': 'becpa',
                'category_slug': 'marketing',
                'title': 'BECPA',
                'definition': 'Break-Even Cost Per Acquisition - Coût maximum que vous pouvez payer pour acquérir un client sans perdre d\'argent.',
                'examples': 'Si votre marge est de 15€, vous ne devez pas dépenser plus de 15€ pour acquérir un client.',
                'context': 'marketing'
            },
            {
                'slug': 'cpc',
                'category_slug': 'publicite-payante',
                'title': 'CPC',
                'definition': 'Coût Par Clic - Prix que vous payez à chaque fois que quelqu\'un clique sur votre publicité.',
                'examples': '',
                'benchmarks': 'Google Ads 0,50€-2€, Facebook Ads 0,30€-1,50€ selon le secteur',
                'context': 'ads'
            },
            {
                'slug': 'cpm',
                'category_slug': 'publicite-payante',
                'title': 'CPM',
                'definition': 'Coût Pour Mille impressions - Prix payé pour 1000 affichages d\'une publicité, indépendamment des clics.',
                'examples': 'CPM Facebook : 5-15€, LinkedIn : 8-25€, YouTube : 3-8€. Idéal pour campagnes de notoriété.',
                'formula': 'CPM = (Budget Campagne / Impressions) × 1000',
                'context': 'ads'
            },
            {
                'slug': 'cogs',
                'category_slug': 'ecommerce',
                'title': 'COGS',
                'definition': 'Cost of Goods Sold - Coût direct de production ou d\'achat de votre produit. N\'inclut pas les frais de livraison ou marketing.',
                'examples': 'Prix d\'achat en dropshipping, matières premières en fabrication, licences en digital',
                'context': 'ecommerce'
            },
            {
                'slug': 'taux-conversion',
                'category_slug': 'ecommerce',
                'title': 'Taux de Conversion',
                'definition': 'Pourcentage de visiteurs qui achètent sur votre site.',
                'formula': '(Nombre de commandes ÷ Nombre de visiteurs) × 100',
                'benchmarks': 'E-commerce moyen 1-3%, Bon site 3-5%, Excellent 5%+',
                'context': 'ecommerce'
            },
            {
                'slug': 'panier-moyen',
                'category_slug': 'ecommerce',
                'title': 'Panier Moyen',
                'definition': 'Montant moyen dépensé par client lors d\'un achat.',
                'formula': 'Chiffre d\'affaires total ÷ Nombre de commandes',
                'examples': 'Pour l\'augmenter : Vente croisée, bundles, frais de port gratuits à partir d\'un seuil',
                'context': 'ecommerce'
            },
            {
                'slug': 'frais-bancaires',
                'category_slug': 'costs',
                'title': 'Frais Bancaires',
                'definition': 'Commission prélevée par votre processeur de paiement sur chaque transaction.',
                'benchmarks': 'Stripe 2,9%, PayPal 3,4%, Banque traditionnelle 1-2%',
                'examples': 'Se calcule généralement sur le montant HT',
                'context': 'finance'
            },
            {
                'slug': 'roi',
                'category_slug': 'marketing',
                'title': 'ROI',
                'definition': 'Return On Investment - Rendement de votre investissement publicitaire. Mesure le profit généré par rapport à ce que vous avez investi.',
                'formula': '((Profit - Investissement) ÷ Investissement) × 100',
                'examples': 'ROI de 200% = vous gagnez 2€ pour chaque 1€ investi',
                'context': 'marketing'
            },
            {
                'slug': 'ltv',
                'category_slug': 'ecommerce',
                'title': 'LTV',
                'definition': 'LifeTime Value - Valeur totale qu\'un client apporte à votre entreprise pendant toute sa relation avec vous.',
                'formula': 'Panier moyen × Nombre d\'achats par an × Durée de vie client',
                'examples': 'SaaS 100€/mois, rétention 24 mois : LTV = 2400€. E-commerce : panier moyen 80€ × 5 achats/an × 3 ans = 1200€.',
                'context': 'ecommerce'
            },
            {
                'slug': 'taux-retour',
                'category_slug': 'ecommerce',
                'title': 'Taux de Retour',
                'definition': 'Pourcentage de commandes retournées par les clients.',
                'benchmarks': 'E-commerce général 5-15%, Mode 20-30%, Électronique 5-10%',
                'examples': 'Réduit votre marge effective, à intégrer dans vos calculs BEROAS',
                'context': 'ecommerce'
            },
            {
                'slug': 'attribution',
                'category_slug': 'marketing',
                'title': 'Attribution',
                'definition': 'Méthode pour attribuer une vente à une source publicitaire quand un client interagit avec plusieurs canaux.',
                'examples': 'Premier clic : Attribue à la première interaction. Dernier clic : Attribue à la dernière interaction. Linéaire : Répartit le crédit entre tous les touchpoints.',
                'context': 'marketing'
            },
            {
                'slug': 'dropshipping',
                'category_slug': 'ecommerce',
                'title': 'Dropshipping',
                'definition': 'Modèle où vous vendez des produits sans les stocker. Le fournisseur expédie directement au client.',
                'examples': 'Avantages : Pas de stock, investissement minimal. Inconvénients : Marges réduites, moins de contrôle qualité.',
                'benchmarks': 'BEROAS typique : 2-3 (marges plus serrées que la vente classique)',
                'context': 'ecommerce'
            }
        ]
        
        for term_data in terms_data:
            self.create_or_update_term(term_data, stats, dry_run, update_existing)

    def create_or_update_term(self, data, stats, dry_run, update_existing):
        """Crée ou met à jour un terme"""
        
        if not dry_run:
            # Récupérer la catégorie
            try:
                category = TermCategory.objects.get(slug=data['category_slug'])
            except TermCategory.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Catégorie non trouvée: {data["category_slug"]} pour {data["slug"]}')
                )
                return
            
            # Créer/mettre à jour le terme
            term, created = Term.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'category': category,
                    'is_essential': True,
                    'difficulty_level': 'beginner',
                    'is_active': True
                }
            )
            
            if created:
                stats['terms_created'] += 1
                action = '✅ Créé'
            elif update_existing:
                term.category = category
                term.is_essential = True
                term.save()
                stats['terms_updated'] += 1
                action = '🔄 Mis à jour'
            else:
                action = '⏭️  Ignoré (existe)'
            
            # Créer/mettre à jour la traduction
            translation, tr_created = TermTranslation.objects.update_or_create(
                term=term,
                language='fr',
                context=data.get('context', ''),
                defaults={
                    'title': data['title'],
                    'definition': data['definition'],
                    'examples': data.get('examples', ''),
                    'formula': data.get('formula', ''),
                    'benchmarks': data.get('benchmarks', '')
                }
            )
            
            if tr_created:
                stats['translations_created'] += 1
            
            self.stdout.write(f'  {action}: {data["title"]} ({data["slug"]})')
        
        else:
            stats['terms_created'] += 1
            stats['translations_created'] += 1

    def create_relations(self, stats, dry_run):
        """Crée les relations logiques entre termes"""
        
        relations = [
            ('beroas', 'roas', 'related'),
            ('beroas', 'marge', 'related'),
            ('cpc', 'cpm', 'related'),
            ('cpc', 'roas', 'related'),
            ('roas', 'roi', 'related'),
            ('ltv', 'taux-retour', 'related'),
            ('taux-conversion', 'panier-moyen', 'related'),
            ('marge', 'taux-marge', 'related'),
            ('cogs', 'marge', 'related'),
        ]
        
        if not dry_run:
            for from_slug, to_slug, relation_type in relations:
                try:
                    from_term = Term.objects.get(slug=from_slug)
                    to_term = Term.objects.get(slug=to_slug)
                    
                    relation, created = TermRelation.objects.get_or_create(
                        from_term=from_term,
                        to_term=to_term,
                        relation_type=relation_type,
                        defaults={'weight': 5}
                    )
                    
                    if created:
                        stats['relations_created'] += 1
                        
                except Term.DoesNotExist:
                    continue
        else:
            stats['relations_created'] = len(relations)

    def print_stats(self, stats):
        """Affiche le rapport final"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RAPPORT D\'IMPORT'))
        self.stdout.write(f'📁 Catégories créées: {stats["categories_created"]}')
        self.stdout.write(f'📝 Termes créés: {stats["terms_created"]}')
        self.stdout.write(f'🔄 Termes mis à jour: {stats["terms_updated"]}')
        self.stdout.write(f'🌍 Traductions créées: {stats["translations_created"]}')
        self.stdout.write(f'🔗 Relations créées: {stats["relations_created"]}')
        self.stdout.write('\n✅ Import terminé avec succès!')