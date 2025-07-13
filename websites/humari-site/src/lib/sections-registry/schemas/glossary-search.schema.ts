// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/glossary-search.schema.ts
import type { SectionSchema } from '../types'

export const glossarySearchSchema: SectionSchema = {
  type: 'glossary_search',
  name: 'Recherche Glossaire',
  category: 'tools',
  description: 'Outil de recherche dans le glossaire business avec filtres avancés',
  icon: '🔍',
  allowMultiple: false,
  props: {
    title: {
      type: 'string',
      label: 'Titre de la section',
      default: 'Recherche dans le Glossaire Business',
      placeholder: 'Titre affiché au-dessus du moteur de recherche'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      rows: 2,
      default: 'Découvrez plus de 300 définitions essentielles du marketing digital, SEO, vente et business.',
      placeholder: 'Description de la section'
    },
    variant: {
      type: 'select',
      label: 'Variante d\'affichage',
      required: true,
      default: 'embedded',
      options: [
        { value: 'full', label: 'Complète (avec titre et footer)' },
        { value: 'embedded', label: 'Intégrée (sans décoration)' },
        { value: 'minimal', label: 'Minimale (compacte)' }
      ]
    },
    show_categories: {
      type: 'boolean',
      label: 'Afficher le filtre par catégorie',
      default: true
    },
    show_popular: {
      type: 'boolean',
      label: 'Afficher les termes populaires',
      default: true
    },
    show_filters: {
      type: 'boolean',
      label: 'Afficher les filtres avancés',
      default: true
    },
    popular_limit: {
      type: 'number',
      label: 'Nombre de termes populaires',
      default: 8,
      helpText: 'Nombre de termes populaires à afficher (si activé)'
    },
    results_per_page: {
      type: 'number',
      label: 'Résultats par page',
      default: 10,
      helpText: 'Nombre de résultats chargés par page'
    },
    auto_search: {
      type: 'boolean',
      label: 'Recherche automatique',
      default: true,
      helpText: 'Lance la recherche automatiquement pendant la saisie'
    },
    placeholder: {
      type: 'string',
      label: 'Placeholder de recherche',
      default: 'Rechercher un terme...',
      placeholder: 'Texte affiché dans le champ de recherche'
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'neutral',
      options: [
        { value: 'transparent', label: 'Transparent' },
        { value: 'white', label: 'Blanc' },
        { value: 'neutral', label: 'Neutre' },
        { value: 'brand', label: 'Couleur de marque' }
      ]
    },
    custom_cta_text: {
      type: 'string',
      label: 'Texte CTA personnalisé',
      placeholder: 'Ex: Découvrir tous nos guides'
    },
    custom_cta_url: {
      type: 'url',
      label: 'URL CTA personnalisé',
      placeholder: 'https://...'
    },
    tracking_id: {
      type: 'string',
      label: 'ID de tracking',
      placeholder: 'Pour analytics/GTM'
    }
  }
}