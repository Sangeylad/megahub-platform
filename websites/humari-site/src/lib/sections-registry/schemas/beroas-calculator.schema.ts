// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/beroas-calculator.schema.ts
import type { SectionSchema } from '../types'

export const beroasCalculatorSchema: SectionSchema = {
  type: 'beroas_calculator',
  name: 'Calculateur BEROAS',
  category: 'tools',
  description: 'Calculateur de seuil de rentabilité publicitaire (Break-Even Return On Ad Spend)',
  icon: '🎯',
  layoutContainer: false,
  props: {
    title: {
      type: 'string',
      label: 'Titre principal',
      required: false,
      default: 'Calculateur BEROAS E-commerce',
      placeholder: 'Calculez votre seuil de rentabilité...'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre/Description',
      required: false,
      default: 'Calculez le seuil de rentabilité de vos campagnes publicitaires',
      rows: 2,
      placeholder: 'Description de l\'outil...'
    },
    initial_tab: {
      type: 'select',
      label: 'Onglet par défaut',
      required: false,
      default: 'basic',
      options: [
        { value: 'basic', label: 'Calculateur Simple' },
        { value: 'advanced', label: 'BEROAS Avancé' },
        { value: 'volume', label: 'Simulateur Volume' },
        { value: 'matrix', label: 'Matrice Interactive' }
      ]
    },
    show_export: {
      type: 'boolean',
      label: 'Afficher le bouton d\'export PDF',
      required: false,
      default: true
    },
    variant: {
      type: 'select',
      label: 'Variante d\'affichage',
      required: false,
      default: 'full',
      options: [
        { value: 'full', label: 'Complet (avec header)' },
        { value: 'embedded', label: 'Intégré (sans header)' },
        { value: 'minimal', label: 'Minimal (basique seulement)' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      required: false,
      default: 'neutral',
      options: [
        { value: 'neutral', label: 'Neutre (gris clair)' },
        { value: 'white', label: 'Blanc' },
        { value: 'brand', label: 'Couleur de marque' },
        { value: 'transparent', label: 'Transparent' }
      ]
    },
    custom_cta_text: {
      type: 'string',
      label: 'Texte CTA personnalisé',
      required: false,
      placeholder: 'Obtenir mon analyse BEROAS...'
    },
    custom_cta_url: {
      type: 'url',
      label: 'URL CTA personnalisé',
      required: false,
      placeholder: 'https://...'
    },
    tracking_id: {
      type: 'string',
      label: 'ID de suivi (analytics)',
      required: false,
      placeholder: 'beroas-calculator-homepage'
    }
  }
}