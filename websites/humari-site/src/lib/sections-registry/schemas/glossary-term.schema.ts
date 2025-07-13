// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/glossary-term.schema.ts
import type { SectionSchema } from '../types'

export const glossaryTermSchema: SectionSchema = {
  type: 'glossary_term',
  name: 'Terme de Glossaire',
  category: 'tools',
  description: 'Affichage d\'un terme spécifique du glossaire avec définition complète',
  icon: '📖',
  allowMultiple: true,
  props: {
    // ✅ Props injectées automatiquement par le backend
    term: {
      type: 'object',
      label: 'Données du terme (auto)',
      internal: true
    },
    slug: {
      type: 'string', 
      label: 'Slug du terme (auto)',
      internal: true
    },
    
    language: {
      type: 'select',
      label: 'Langue',
      default: 'fr',
      options: [
        { value: 'fr', label: 'Français' },
        { value: 'en', label: 'Anglais' }
      ]
    },
    showRelated: {
      type: 'boolean',
      label: 'Afficher les termes connexes',
      default: true
    },
    showBreadcrumb: {
      type: 'boolean',
      label: 'Afficher le fil d\'Ariane',
      default: true
    },
    showMetadata: {
      type: 'boolean',
      label: 'Afficher les métadonnées',
      default: true,
      helpText: 'Catégorie, auteur, date de mise à jour'
    },
    hideNavigation: {
      type: 'boolean',
      label: 'Masquer la navigation',
      default: false
    },
    customTitle: {
      type: 'string',
      label: 'Titre personnalisé',
      placeholder: 'Remplace le titre par défaut du terme'
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'white',
      options: [
        { value: 'transparent', label: 'Transparent' },
        { value: 'white', label: 'Blanc' },
        { value: 'neutral', label: 'Neutre' },
        { value: 'gradient', label: 'Dégradé' }
      ]
    },
    padding: {
      type: 'select',
      label: 'Espacement',
      default: 'normal',
      options: [
        { value: 'none', label: 'Aucun' },
        { value: 'small', label: 'Petit' },
        { value: 'normal', label: 'Normal' },
        { value: 'large', label: 'Grand' }
      ]
    },
    maxWidth: {
      type: 'select',
      label: 'Largeur maximale',
      default: '4xl',
      options: [
        { value: '3xl', label: 'Petite (3xl)' },
        { value: '4xl', label: 'Normale (4xl)' },
        { value: '5xl', label: 'Grande (5xl)' },
        { value: '6xl', label: 'Très grande (6xl)' },
        { value: 'full', label: 'Pleine largeur' }
      ]
    },
    relatedLimit: {
      type: 'number',
      label: 'Limite termes connexes',
      default: 6,
      helpText: 'Nombre maximum de termes connexes à afficher'
    },
    cta_text: {
      type: 'string',
      label: 'Texte du CTA',
      placeholder: 'Ex: Découvrir nos services'
    },
    cta_url: {
      type: 'url',
      label: 'URL du CTA',
      placeholder: 'https://...'
    },
    cta_variant: {
      type: 'select',
      label: 'Style du CTA',
      default: 'primary',
      options: [
        { value: 'primary', label: 'Principal' },
        { value: 'secondary', label: 'Secondaire' },
        { value: 'outline', label: 'Contour' }
      ]
    },
    customCSS: {
      type: 'text',
      label: 'CSS personnalisé',
      rows: 4,
      placeholder: '.glossary-term-content { ... }',
      helpText: 'CSS additionnel pour personnaliser l\'affichage'
    },
    tracking_event: {
      type: 'string',
      label: 'Événement de tracking',
      placeholder: 'glossary_term_view'
    },
    tracking_category: {
      type: 'string',
      label: 'Catégorie de tracking',
      default: 'Glossaire'
    },
    tracking_params: {
      type: 'text',
      label: 'Paramètres de tracking (JSON)',
      rows: 2,
      placeholder: '{"source": "page_name", "custom": "value"}'
    }
  }
}