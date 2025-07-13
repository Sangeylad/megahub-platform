// /var/www/megahub/websites/humari-site/src/lib/sections-registry/validator.ts
import { SectionsRegistry } from './index'

export interface ValidationResult {
  isValid: boolean
  errors: string[]
  sanitizedData: Record<string, unknown>
}

export class SectionValidator {
  
  static validateSectionData(type: string, data: unknown): ValidationResult {
    const schema = SectionsRegistry.getSectionSchema(type)
    if (!schema) {
      return {
        isValid: false,
        errors: [`Schema non trouvé pour le type "${type}"`],
        sanitizedData: {}
      }
    }

    const errors: string[] = []
    const sanitizedData: Record<string, unknown> = {}

    // Vérifier que data est un objet
    if (typeof data !== 'object' || data === null) {
      return {
        isValid: false,
        errors: ['Les données doivent être un objet'],
        sanitizedData: {}
      }
    }

    const dataObj = data as Record<string, unknown>

    // ✅ NOUVEAU : Préserver les props internes AVANT validation
    for (const [propKey, propSchema] of Object.entries(schema.props)) {
      if (propSchema.internal && dataObj[propKey] !== undefined) {
        sanitizedData[propKey] = dataObj[propKey]
      }
    }

    // Valider chaque propriété requise
    for (const [propKey, propSchema] of Object.entries(schema.props)) {
      const value = dataObj[propKey]
      
      // ✅ NOUVEAU : Skip les props internes (déjà traitées)
      if (propSchema.internal) continue
      
      // Vérifier si la propriété requise est présente
      if (propSchema.required && (value === undefined || value === null || value === '')) {
        errors.push(`"${propSchema.label}" est requis`)
        continue
      }

      // Si on a une valeur, l'inclure
      if (value !== undefined && value !== null) {
        sanitizedData[propKey] = value
      }
      // Sinon, utiliser la valeur par défaut si elle existe
      else if (propSchema.default !== undefined) {
        sanitizedData[propKey] = propSchema.default
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      sanitizedData
    }
  }

  // Méthode pour valider des types spécifiques
  static validateSpecificType<T>(
    type: string, 
    data: unknown, 
    typeGuard: (data: unknown) => data is T
  ): { isValid: boolean; errors: string[]; data?: T } {
    
    const baseValidation = this.validateSectionData(type, data)
    
    if (!baseValidation.isValid) {
      return {
        isValid: false,
        errors: baseValidation.errors
      }
    }

    if (typeGuard(baseValidation.sanitizedData)) {
      return {
        isValid: true,
        errors: [],
        data: baseValidation.sanitizedData
      }
    }

    return {
      isValid: false,
      errors: [`Les données ne correspondent pas au type attendu pour "${type}"`]
    }
  }
}