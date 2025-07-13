// src/components/tools/glossary-search/utils/formatters.ts
import { GlossaryTerm, TermTranslation } from '../types'

export const formatters = {
  // Récupérer la traduction principale d'un terme
  getPrimaryTranslation: (term: GlossaryTerm): TermTranslation | null => {
    return term.primary_translation || 
           term.current_translation || 
           term.translations?.[0] || 
           null
  },
  
  // Tronquer le texte avec points de suspension
  truncateText: (text: string, maxLength: number): string => {
    if (!text || text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  },
  
  // Formater la difficulté en français
  formatDifficulty: (difficulty: string): string => {
    const levels = {
      'beginner': 'Débutant',
      'intermediate': 'Intermédiaire', 
      'advanced': 'Avancé'
    }
    return levels[difficulty as keyof typeof levels] || difficulty
  },
  
  // ✅ NOUVELLE FONCTION : Difficulté avec emojis
  formatDifficultyWithEmoji: (level: string): string => {
    const levels: Record<string, string> = {
      'beginner': '🟢 Débutant',
      'débutant': '🟢 Débutant',
      'intermediate': '🟡 Intermédiaire', 
      'intermédiaire': '🟡 Intermédiaire',
      'advanced': '🔴 Avancé',
      'avancé': '🔴 Avancé',
      'expert': '⚫ Expert'
    }
    return levels[level.toLowerCase()] || `📚 ${level}`
  },
  
  // URL pour les termes
  getTermUrl: (term: GlossaryTerm): string => {
    return `/glossaire/definition-${term.slug}/`
  },
  
  // Formater le score de popularité
  formatPopularityScore: (score: number): string => {
    if (score >= 1000) return `${Math.round(score / 100) / 10}k`
    return score.toString()
  },
  
  // Highlighting des résultats de recherche
  highlightSearchTerm: (text: string, searchTerm: string): string => {
    if (!searchTerm || !text) return text
    
    const regex = new RegExp(`(${searchTerm})`, 'gi')
    return text.replace(regex, '<mark>$1</mark>')
  },
  
  // Extraire le nom d'affichage d'un terme
  getDisplayTitle: (term: GlossaryTerm): string => {
    const translation = formatters.getPrimaryTranslation(term)
    return translation?.title || term.title || 'Terme sans titre'
  },
  
  // Extraire la définition d'affichage
  getDisplayDefinition: (term: GlossaryTerm): string => {
    const translation = formatters.getPrimaryTranslation(term)
    return translation?.definition || term.definition || ''
  },
  
  // Extraire les exemples d'affichage
  getDisplayExamples: (term: GlossaryTerm): string => {
    const translation = formatters.getPrimaryTranslation(term)
    return translation?.examples || term.examples || ''
  }
}