// /var/www/megahub/websites/humari-site/src/lib/sections-registry/types.ts
export type SectionPropType =
  | 'string'
  | 'text'
  | 'boolean'
  | 'select'
  | 'number'
  | 'url'
  | 'color'
  | 'object'  // ✅ AJOUTÉ
  | 'stats_array'
  | 'services_array'
  | 'testimonials_array'
  | 'fields_array'
  | 'navigation_array'
  | 'group'

export interface SelectOption {
  value: string
  label: string
}

export interface ArrayItemSchema {
  type: 'string' | 'text' | 'number' | 'boolean' | 'select' | 'url'
  label: string
  required?: boolean
  placeholder?: string
  options?: SelectOption[]
  rows?: number
}

// ✅ Types stricts au lieu de any
export type SectionPropDefaultValue =
  | string
  | number
  | boolean
  | SelectOption[]
  | Record<string, unknown>[]

export interface SectionPropSchema {
  type: SectionPropType
  label: string
  required?: boolean
  default?: SectionPropDefaultValue
  options?: SelectOption[]
  rows?: number
  placeholder?: string
  helpText?: string
  internal?: boolean  // ✅ AJOUTÉ
  // Pour les arrays complexes
  itemSchema?: Record<string, ArrayItemSchema>
  maxItems?: number
  minItems?: number
  addButtonText?: string
  removeButtonText?: string
  // 🆕 Pour les sections fixes
  isFixed?: boolean // Header/Footer non supprimables
  conditionalOn?: string // Affichage conditionnel basé sur une autre prop
}

export interface SectionSchema {
  type: string
  name: string
  category: string
  description: string
  icon?: string
  props: Record<string, SectionPropSchema>
  layoutContainer?: boolean
  // 🆕 Métadonnées supplémentaires
  isFixed?: boolean // Section non supprimable (header/footer)
  allowMultiple?: boolean // Peut avoir plusieurs instances sur une page
  requiredProps?: string[] // Props obligatoires pour validation rapide
}