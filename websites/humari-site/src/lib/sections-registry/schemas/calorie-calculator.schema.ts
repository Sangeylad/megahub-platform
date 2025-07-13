import type { SectionSchema } from '../types'

export const calorieCalculatorSchema: SectionSchema = {
  type: 'calorie_calculator',
  name: 'Calculateur de Calories',
  category: 'tools',
  description: 'Outil de calcul des besoins caloriques personnalisés avec export PDF',
  icon: '🧮',
  allowMultiple: false,
  props: {
    title: {
      type: 'string',
      label: 'Titre principal',
      placeholder: 'Ex: Calculez vos besoins caloriques',
      helpText: 'Titre affiché au-dessus du calculateur'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      placeholder: 'Ex: Outil gratuit et précis pour optimiser votre nutrition',
      rows: 2,
      helpText: 'Description courte sous le titre'
    },
    initial_tab: {
      type: 'select',
      label: 'Onglet par défaut',
      required: true,
      default: 'basic',
      options: [
        { value: 'basic', label: 'Calcul Rapide' },
        { value: 'advanced', label: 'Calcul Précis' },
        { value: 'results', label: 'Résultats' }
      ],
      helpText: 'Onglet affiché à l\'ouverture de la page'
    },
    show_export: {
      type: 'boolean',
      label: 'Afficher l\'export PDF',
      default: true,
      helpText: 'Permet aux utilisateurs de télécharger leurs résultats en PDF'
    },
    variant: {
      type: 'select',
      label: 'Variante d\'affichage',
      required: true,
      default: 'embedded',
      options: [
        { value: 'full', label: 'Complet' },
        { value: 'embedded', label: 'Intégré' },
        { value: 'minimal', label: 'Minimal' }
      ],
      helpText: 'Style et taille du calculateur'
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      required: true,
      default: 'neutral',
      options: [
        { value: 'neutral', label: 'Neutre' },
        { value: 'white', label: 'Blanc' },
        { value: 'brand', label: 'Couleur de marque' },
        { value: 'transparent', label: 'Transparent' }
      ]
    },
    custom_cta_text: {
      type: 'string',
      label: 'Texte CTA personnalisé',
      placeholder: 'Ex: Obtenir un coaching personnalisé',
      helpText: 'Bouton d\'action affiché après les résultats (optionnel)'
    },
    custom_cta_url: {
      type: 'url',
      label: 'URL du CTA personnalisé',
      placeholder: 'Ex: /contact',
      helpText: 'Lien vers lequel redirige le CTA'
    },
    tracking_id: {
      type: 'string',
      label: 'ID de tracking',
      placeholder: 'Ex: calorie-calc-homepage',
      helpText: 'Identifiant pour le tracking analytics (optionnel)',
      internal: true
    }
  }
}