// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/features-grid.schema.ts
import { SectionSchema } from '../types'
import { COLUMNS_OPTIONS } from '../utils/defaults'

export const featuresSchema: SectionSchema = {
  type: "features_grid",
  name: "Grille de Fonctionnalités",
  category: "content",
  description: "Grille simple présentant des fonctionnalités",
  icon: "⚡",
  props: {
    title: {
      type: 'string',
      label: 'Titre',
      placeholder: 'Nos Fonctionnalités'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      rows: 2,
      placeholder: 'Ce qui nous distingue'
    },
    columns: {
      type: 'select',
      label: 'Nombre de colonnes',
      default: '3',
      options: COLUMNS_OPTIONS
    }
  }
}