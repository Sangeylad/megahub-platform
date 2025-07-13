// src/components/tools/glossary-search/index.ts
export { TermDisplay } from './components/TermDisplay'
export { TermHeader } from './components/TermHeader'
export { TermContent } from './components/TermContent'
export { RelatedTerms } from './components/RelatedTerms'
export { useTermDisplay } from './hooks/useTermDisplay'

// Re-export des types pour simplifier les imports
export type {
  GlossaryTerm,
  TermTranslation,
  GlossaryCategory,
  SearchParams,
  SearchResults,
  TermDisplayProps,
  TermMetadata
} from './types'