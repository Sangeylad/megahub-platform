// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/services-grid.schema.ts
import { SectionSchema } from '../types'
import { SERVICES_ARRAY_SCHEMA } from '../utils/array-schemas'
import { HUMARI_SERVICES_DEFAULT, VARIANT_OPTIONS, BACKGROUND_OPTIONS, COLUMNS_OPTIONS } from '../utils/defaults'

export const servicesSchema: SectionSchema = {
  type: "services_grid",
  name: "Grille de Services",
  category: "content",
  description: "Grille présentant vos services avec cartes interactives",
  icon: "🛠️",
  props: {
    title: {
      type: 'string',
      label: 'Titre de la section',
      placeholder: 'Nos Services'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      rows: 2,
      placeholder: 'Description de vos services'
    },
    services: {
      ...SERVICES_ARRAY_SCHEMA,
      default: HUMARI_SERVICES_DEFAULT
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
        { value: 'masonry', label: 'Masonry' },
        { value: 'carousel', label: 'Carrousel' },
        { value: 'alternating', label: 'Alterné' }
      ]
    },
    card_style: {
      type: 'select',
      label: 'Style de carte',
      default: 'elevated',
      required: true,
      options: [
        { value: 'flat', label: 'Plat' },
        { value: 'elevated', label: 'Élevé' },
        { value: 'bordered', label: 'Bordure' },
        { value: 'gradient', label: 'Gradient' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'transparent',
      required: true,
      options: BACKGROUND_OPTIONS
    },
    columns: {
      type: 'select',
      label: 'Nombre de colonnes',
      default: '3',
      required: true,
      options: COLUMNS_OPTIONS
    },
    show_cta: {
      type: 'boolean',
      label: 'Afficher les CTA',
      default: true,
      required: true
    }
  }
}