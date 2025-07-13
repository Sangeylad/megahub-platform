// lib/sections-registry/index.ts - COMPLET CORRIGÉ STRICT
import { SectionSchema } from './types'
import * as schemas from './schemas'

export class SectionsRegistry {
  
  static getAllSections(): SectionSchema[] {
    // ✅ CORRIGÉ : Filtrer seulement les vrais SectionSchema
    return Object.values(schemas).filter((schema): schema is SectionSchema => 
      typeof schema === 'object' && 
      schema !== null && 
      'type' in schema && 
      'name' in schema && 
      'category' in schema && 
      'props' in schema
    )
  }

  static getSectionSchema(type: string): SectionSchema | undefined {
    return this.getAllSections().find(section => section.type === type)
  }

  static getSectionsByCategory(category: string): SectionSchema[] {
    return this.getAllSections().filter(section => section.category === category)
  }

  static getLayoutContainers(): SectionSchema[] {
    return this.getAllSections().filter(section => section.layoutContainer === true)
  }

  static getContentSections(): SectionSchema[] {
    return this.getAllSections().filter(section => section.layoutContainer !== true)
  }

  static getHeaderSections(): SectionSchema[] {
    return this.getAllSections().filter(section => section.category === 'layout' && section.type === 'header')
  }

  static getFooterSections(): SectionSchema[] {
    return this.getAllSections().filter(section => section.category === 'layout' && section.type === 'footer')
  }

  static getToolsSections(): SectionSchema[] {
    return this.getAllSections().filter(section => 
      section.category === 'tools' || 
      section.type === 'tools_listing' ||
      section.type.includes('calculator')
    )
  }

  static getGlossarySections(): SectionSchema[] {
    return this.getAllSections().filter(section => 
      section.category === 'glossary' || 
      section.type.startsWith('glossary_')
    )
  }

  static getCategorizedSections(): Record<string, SectionSchema[]> {
    const sections = this.getAllSections()
    const categories: Record<string, SectionSchema[]> = {}

    sections.forEach(section => {
      const category = section.category
      if (!categories[category]) {
        categories[category] = []
      }
      categories[category].push(section)
    })

    return categories
  }

  // ✅ CORRIGÉ : Gestion stricte des types optionnels
  static getCategorizedSectionsWithMeta(): Record<string, {
    sections: SectionSchema[],
    count: number,
    description?: string
  }> {
    const categorized = this.getCategorizedSections()
    const result: Record<string, { sections: SectionSchema[], count: number, description?: string }> = {}

    // Descriptions des catégories
    const categoryDescriptions: Record<string, string> = {
      'hero': 'Sections d\'en-tête et bannières principales',
      'content': 'Sections de contenu principal',
      'cta': 'Appels à l\'action et conversion',
      'layout': 'Containers et structures de mise en page',
      'forms': 'Formulaires et interactions utilisateur',
      'tools': 'Outils et calculateurs interactifs',
      'glossary': 'Sections liées au glossaire',
      'navigation': 'Éléments de navigation'
    }

    Object.entries(categorized).forEach(([category, sections]) => {
      const description = categoryDescriptions[category]
      
      // ✅ CORRIGÉ : N'inclure description que si elle existe
      result[category] = description ? {
        sections,
        count: sections.length,
        description
      } : {
        sections,
        count: sections.length
      }
    })

    return result
  }

  static validateSectionProps(type: string, props: Record<string, unknown>): { isValid: boolean; errors: string[] } {
    const schema = this.getSectionSchema(type)
    if (!schema) {
      return { isValid: false, errors: [`Section type "${type}" not found`] }
    }

    const errors: string[] = []

    Object.entries(schema.props).forEach(([propName, propSchema]) => {
      if (propSchema.required && (props[propName] === undefined || props[propName] === '')) {
        errors.push(`Property "${propName}" is required`)
      }
    })

    return { isValid: errors.length === 0, errors }
  }

  static getDefaultProps(type: string): Record<string, unknown> {
    const schema = this.getSectionSchema(type)
    if (!schema) {
      return {}
    }

    const defaultProps: Record<string, unknown> = {}

    Object.entries(schema.props).forEach(([propName, propSchema]) => {
      if (propSchema.default !== undefined) {
        defaultProps[propName] = propSchema.default
      }
    })

    return defaultProps
  }

  static isFixedSection(type: string): boolean {
    return type === 'header' || type === 'footer'
  }

  static isInteractiveSection(type: string): boolean {
    const interactiveSections = [
      'contact_form',
      'calorie_calculator', 
      'beroas_calculator',
      'tools_listing',
      'glossary_search'
    ]
    return interactiveSections.includes(type)
  }

  static requiresExternalData(type: string): boolean {
    const externalDataSections = [
      'tools_listing',
      'glossary_term',
      'glossary_search'
    ]
    return externalDataSections.includes(type)
  }

  static getAvailableVariants(type: string): Array<{ value: string; label: string }> {
    const schema = this.getSectionSchema(type)
    if (!schema || !schema.props.variant || schema.props.variant.type !== 'select') {
      return []
    }

    return schema.props.variant.options || []
  }

  static searchSections(query: string): SectionSchema[] {
    const lowercaseQuery = query.toLowerCase()
    return this.getAllSections().filter(section => 
      section.name.toLowerCase().includes(lowercaseQuery) ||
      section.description.toLowerCase().includes(lowercaseQuery) ||
      section.type.toLowerCase().includes(lowercaseQuery) ||
      section.category.toLowerCase().includes(lowercaseQuery)
    )
  }

  static getSectionsCompatibleWithLayout(): SectionSchema[] {
    return this.getContentSections()
  }

  static getRegistryStats(): {
    total_sections: number,
    categories: Record<string, number>,
    interactive_sections: number,
    layout_containers: number,
    content_sections: number,
    external_data_sections: number
  } {
    const allSections = this.getAllSections()
    const categorized = this.getCategorizedSections()
    
    const categories: Record<string, number> = {}
    Object.entries(categorized).forEach(([category, sections]) => {
      categories[category] = sections.length
    })

    return {
      total_sections: allSections.length,
      categories,
      interactive_sections: allSections.filter(s => this.isInteractiveSection(s.type)).length,
      layout_containers: this.getLayoutContainers().length,
      content_sections: this.getContentSections().length,
      external_data_sections: allSections.filter(s => this.requiresExternalData(s.type)).length
    }
  }

  static getRecommendedSections(context: {
    page_type?: string,
    existing_sections?: string[],
    target_audience?: string
  }): SectionSchema[] {
    const { page_type, existing_sections = [] } = context
    
    const recommendations: Record<string, string[]> = {
      'landing': ['hero_banner', 'cta_banner', 'contact_form', 'features_grid'],
      'blog': ['hero_banner', 'rich_text', 'cta_banner'],
      'outils': ['hero_banner', 'tools_listing', 'contact_form'],
      'about': ['hero_banner', 'rich_text', 'features_grid'],
      'contact': ['hero_banner', 'contact_form']
    }

    const recommendedTypes = recommendations[page_type || 'landing'] || []
    const filteredTypes = recommendedTypes.filter(type => !existing_sections.includes(type))
    
    return filteredTypes
      .map(type => this.getSectionSchema(type))
      .filter((schema): schema is SectionSchema => schema !== undefined)
  }
}

export type { SectionSchema, SectionPropSchema, SelectOption, ArrayItemSchema } from './types'
export { SectionValidator } from './validator'

export const SECTION_CATEGORIES = {
  HERO: 'hero',
  CONTENT: 'content',
  CTA: 'cta',
  LAYOUT: 'layout',
  FORMS: 'forms',
  TOOLS: 'tools',
  GLOSSARY: 'glossary',
  NAVIGATION: 'navigation'
} as const

export const INTERACTIVE_SECTION_TYPES = [
  'contact_form',
  'calorie_calculator',
  'beroas_calculator', 
  'tools_listing',
  'glossary_search'
] as const

export const EXTERNAL_DATA_SECTION_TYPES = [
  'tools_listing',
  'glossary_term',
  'glossary_search'
] as const