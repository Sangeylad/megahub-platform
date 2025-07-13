// src/components/tools/glossary-search/types/index.ts
export interface GlossaryTerm {
  id: number
  slug: string
  title: string
  definition: string
  examples?: string
  formula?: string
  category: GlossaryCategory
  is_essential: boolean
  popularity_score: number
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  primary_translation?: TermTranslation
  current_translation?: TermTranslation
  translations: TermTranslation[]
  related_terms?: GlossaryTerm[]
}

export interface TermTranslation {
  title: string
  definition: string
  examples?: string
  formula?: string
  language: string
  context?: string
}

export interface GlossaryCategory {
  id: number
  slug: string
  name: string
  description?: string
  parent?: GlossaryCategory
  children?: GlossaryCategory[]
  terms_count?: number
}

export interface SearchFilters {
  query: string
  category: string
  language: string
  essential_only: boolean
  difficulty: string
}

export interface SearchResults {
  results: GlossaryTerm[]
  count: number
  next?: string
  previous?: string
}

export interface SearchParams {
  q?: string
  lang?: string
  category?: string
  essential?: boolean
  difficulty?: string
  page_size?: number
  page?: number
}

export interface GlossarySearchProps {
  variant?: 'full' | 'embedded' | 'minimal'
  show_categories?: boolean
  show_popular?: boolean
  show_filters?: boolean
  popular_limit?: number
  results_per_page?: number
  auto_search?: boolean
  placeholder?: string
  className?: string
}

// ✅ PROPS CORRIGÉES : Suppression de showSuggestions
export interface TermDisplayProps {
  slug: string
  language?: string
  showRelated?: boolean
  showBreadcrumb?: boolean
  className?: string
}

export interface TermMetadata {
  readingTime: number
  wordCount: number
  lastUpdated: string
  difficulty: string
  category: string
}