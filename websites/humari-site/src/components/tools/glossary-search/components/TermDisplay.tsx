// src/components/tools/glossary-search/components/TermDisplay.tsx
'use client'

import Link from 'next/link'
import { TermHeader } from './TermHeader'
import { TermContent } from './TermContent'
import { RelatedTerms } from './RelatedTerms'
import { useTermDisplay } from '../hooks/useTermDisplay'
import type { GlossaryTerm } from '../types'

// ✅ NOUVEAU TYPE POUR DONNÉES INJECTÉES
interface TermDisplayData {
  slug: string
  title: string
  definition: string
  examples?: string
  formula?: string
  benchmarks?: string
  sources?: string
  category: {
    name: string
    slug: string
    color: string
    description: string
  }
  difficulty_level: string
  is_essential: boolean
  popularity_score: number
  meta_title: string
  meta_description: string
  related_terms: Array<{
    slug: string
    title: string
    relation_type: string
  }>
}

// ✅ NOUVEAU TYPE PROPS (TYPES EXPLICITES POUR exactOptionalPropertyTypes)
interface TermDisplayComponentProps {
  // ✅ CORRECTION : Types explicites avec undefined
  termData?: TermDisplayData | undefined
  slug?: string | undefined
  
  language?: string
  showRelated?: boolean
  showBreadcrumb?: boolean
  relatedLimit?: number
  className?: string
}

export function TermDisplay({ 
  termData,
  slug,
  language = 'fr',
  showRelated = true,
  showBreadcrumb = true,
  relatedLimit = 5,
  className = '' 
}: TermDisplayComponentProps) {
  
  // ✅ LOGIQUE HYBRIDE : Utiliser données injectées OU fetch
  const shouldFetch = !termData && !!slug
  const { 
    term: fetchedTerm, 
    relatedTerms: fetchedRelated, 
    isLoading, 
    error, 
    notFound 
  } = useTermDisplay(shouldFetch ? slug! : '', language, { enabled: shouldFetch })

  // ✅ DÉTERMINER LA SOURCE DE DONNÉES
  const term = termData ? convertToGlossaryTerm(termData) : fetchedTerm
  const relatedTerms = termData?.related_terms ? 
    convertRelatedTerms(termData.related_terms) : 
    fetchedRelated.slice(0, relatedLimit)

  console.log('📖 TermDisplay Mode:', termData ? 'Données injectées' : 'Fetch API')
  console.log('📖 Term disponible:', !!term)

  // ✅ LOADING (seulement si on fetch)
  if (shouldFetch && isLoading) {
    return (
      <div className={`max-w-4xl mx-auto ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-neutral-200 rounded mb-4 w-1/3"></div>
          <div className="h-12 bg-neutral-200 rounded mb-6 w-2/3"></div>
          <div className="space-y-3">
            <div className="h-4 bg-neutral-200 rounded w-full"></div>
            <div className="h-4 bg-neutral-200 rounded w-3/4"></div>
            <div className="h-4 bg-neutral-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    )
  }
  
  // ✅ NOT FOUND
  if ((shouldFetch && notFound) || (!termData && !term)) {
    return (
      <div className={`max-w-4xl mx-auto text-center py-12 ${className}`}>
        <div className="space-y-4">
          <div className="text-6xl mb-4">🔍</div>
          <h1 className="text-2xl font-bold text-neutral-800">
            Terme non trouvé
          </h1>
          <p className="text-neutral-600 max-w-md mx-auto">
            Le terme que vous recherchez n&apos;existe pas ou a été supprimé.
          </p>
          <Link
            href="/glossaire"
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg transition-colors"
          >
            ← Retour au glossaire
          </Link>
        </div>
      </div>
    )
  }
  
  // ✅ ERROR (seulement si on fetch)
  if (shouldFetch && error) {
    return (
      <div className={`max-w-4xl mx-auto text-center py-12 ${className}`}>
        <div className="space-y-4">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-neutral-800">
            Erreur de chargement
          </h1>
          <p className="text-neutral-600 max-w-md mx-auto">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-2 px-4 py-2 bg-neutral-600 hover:bg-neutral-700 text-white rounded-lg transition-colors"
          >
            🔄 Réessayer
          </button>
        </div>
      </div>
    )
  }

  if (!term) return null

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <TermHeader 
        term={term} 
        showBreadcrumb={showBreadcrumb}
        className="mb-8"
      />
      
      <TermContent 
        term={term}
        className="mb-12"
      />
      
      {showRelated && relatedTerms.length > 0 && (
        <RelatedTerms 
          terms={relatedTerms}
          currentTermId={term.id}
          className="mb-12"
        />
      )}
      
      <div className="border-t border-neutral-200 pt-8">
  <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
    <Link
      href="/glossaire"
      className="inline-flex items-center gap-2 px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg transition-colors"
    >
      ← Retour au glossaire
    </Link>
    
    {/* ✅ CORRIGÉ : Même logique que le breadcrumb */}
    <Link
      href={`/glossaire?category=${term.category.slug}`}
      className="inline-flex items-center gap-2 px-4 py-2 bg-brand-100 hover:bg-brand-200 text-brand-700 rounded-lg transition-colors"
    >
      Voir la catégorie {term.category.name} →
    </Link>
  </div>
</div>
    </div>
  )
}

// ✅ HELPERS DE CONVERSION (TYPES STRICTS CONFORMES)
function convertToGlossaryTerm(termData: TermDisplayData): GlossaryTerm {
  return {
    id: 0,
    slug: termData.slug,
    title: termData.title,
    definition: termData.definition,
    examples: termData.examples || '',
    difficulty_level: termData.difficulty_level as 'beginner' | 'intermediate' | 'advanced',
    is_essential: termData.is_essential,
    popularity_score: termData.popularity_score,
    
    category: {
      id: 0,
      name: termData.category.name,
      slug: termData.category.slug,
      description: termData.category.description
    },
    
    translations: [],
    
    // ✅ STRICTEMENT conforme à TermTranslation
    primary_translation: {
      language: 'fr',
      title: termData.title,
      definition: termData.definition,
      examples: termData.examples || '',
      formula: termData.formula || ''
    }
  }
}

function convertRelatedTerms(relatedData: Array<{slug: string, title: string, relation_type: string}>): GlossaryTerm[] {
  return relatedData.map((related, index) => ({
    id: index + 1000,
    slug: related.slug,
    title: related.title,
    definition: '',
    difficulty_level: 'intermediate' as const,
    is_essential: false,
    popularity_score: 0,
    
    category: { 
      id: 0,
      name: '', 
      slug: '', 
      description: ''
    },
    
    translations: [],
    
    // ✅ STRICTEMENT conforme à TermTranslation
    primary_translation: {
      language: 'fr',
      title: related.title,
      definition: '',
      examples: '',
      formula: ''
    }
  }))
}