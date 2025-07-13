// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/layout-columns.schema.ts
import { SectionSchema } from '../types'

export const layoutColumnsSchema: SectionSchema = {
  type: "layout_columns",
  name: "Layout Colonnes", 
  category: "layout",
  description: "Container pour organiser le contenu en colonnes CSS Grid",
  icon: "📐",
  layoutContainer: true,
  props: {
    columns: {
      type: 'select',
      label: 'Disposition des colonnes',
      required: true,
      default: '[6, 6]',
      options: [
        { value: '[12]', label: '1 colonne (12/12)' },
        { value: '[6, 6]', label: '2 colonnes égales (6/6)' },
        { value: '[8, 4]', label: '2 colonnes (8/4)' },
        { value: '[4, 8]', label: '2 colonnes (4/8)' },
        { value: '[4, 4, 4]', label: '3 colonnes égales (4/4/4)' },
        { value: '[3, 6, 3]', label: '3 colonnes (3/6/3)' },
        { value: '[3, 3, 3, 3]', label: '4 colonnes égales (3/3/3/3)' }
      ]
    },
    gap: {
      type: 'select',
      label: 'Espacement entre colonnes',
      default: '2rem',
      options: [
        { value: '1rem', label: 'Petit (1rem)' },
        { value: '2rem', label: 'Moyen (2rem)' },
        { value: '3rem', label: 'Grand (3rem)' },
        { value: '4rem', label: 'Très grand (4rem)' }
      ]
    },
    align_items: {
      type: 'select',
      label: 'Alignement vertical',
      default: 'start',
      options: [
        { value: 'start', label: 'Haut' },
        { value: 'center', label: 'Centre' },
        { value: 'end', label: 'Bas' }
      ]
    }
  }
}