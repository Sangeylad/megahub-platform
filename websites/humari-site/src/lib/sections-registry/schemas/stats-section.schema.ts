import { SectionSchema } from '../types'
import { STATS_ARRAY_SCHEMA } from '../utils/array-schemas'
import { VARIANT_OPTIONS, BACKGROUND_OPTIONS } from '../utils/defaults'

// 🧪 DEBUG : Tester les imports
console.log('🔍 STATS_ARRAY_SCHEMA:', STATS_ARRAY_SCHEMA)
console.log('🔍 Is undefined?', STATS_ARRAY_SCHEMA === undefined)

export const statsSchema: SectionSchema = {
  type: "stats_section",
  name: "Section Statistiques",
  category: "content", 
  description: "Affichage de métriques importantes",
  icon: "📊",
  props: {
    title: {
      type: 'string',
      label: 'Titre',
      placeholder: 'Nos Chiffres'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      rows: 2,
      placeholder: 'Des résultats qui parlent'
    },
    // 🚨 SOLUTION DE FORCE : Définition inline complète
    stats: {
      type: 'stats_array',
      label: 'Statistiques',
      required: true,
      minItems: 1,
      maxItems: 6,
      addButtonText: 'Ajouter une statistique',
      removeButtonText: 'Supprimer',
      default: [
        {
          number: "+150",
          label: "Clients",
          description: "Clients accompagnés depuis 2019",
          icon: "👥"
        },
        {
          number: "4.9/5",
          label: "Satisfaction",
          description: "Note moyenne clients",
          icon: "⭐"
        }
      ],
      itemSchema: {
        number: {
          type: 'string',
          label: 'Nombre/Métrique',
          required: true,
          placeholder: '+150'
        },
        label: {
          type: 'string',
          label: 'Label',
          required: true,
          placeholder: 'Clients'
        },
        description: {
          type: 'text',
          label: 'Description',
          placeholder: 'Clients satisfaits depuis 2019',
          rows: 2
        },
        icon: {
          type: 'string',
          label: 'Icône (emoji)',
          placeholder: '👥'
        }
      }
    },
    variant: {
      type: 'select',
      label: 'Variante',
      default: 'standard',
      required: true,
      options: VARIANT_OPTIONS
    },
    layout: {
      type: 'select',
      label: 'Layout',
      default: 'grid',
      required: true,
      options: [
        { value: 'grid', label: 'Grille' },
        { value: 'inline', label: 'En ligne' },
        { value: 'cards', label: 'Cartes' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'transparent',
      required: true,
      options: BACKGROUND_OPTIONS
    },
    animation: {
      type: 'select',
      label: 'Animation',
      default: 'reveal',
      required: true,
      options: [
        { value: 'none', label: 'Aucune' },
        { value: 'counter', label: 'Compteur' },
        { value: 'reveal', label: 'Révélation' }
      ]
    }
  }
}

// 🧪 DEBUG : Vérifier le résultat
console.log('🔍 Final props keys:', Object.keys(statsSchema.props))
console.log('🔍 Has stats prop:', 'stats' in statsSchema.props)