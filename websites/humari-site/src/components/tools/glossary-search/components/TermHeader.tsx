// src/components/tools/glossary-search/components/TermHeader.tsx
'use client'

import Link from 'next/link'
import { formatters } from '../utils/formatters'
import type { GlossaryTerm } from '../types'

interface TermHeaderProps {
  term: GlossaryTerm
  showBreadcrumb?: boolean
  className?: string
}

export function TermHeader({
  term,
  showBreadcrumb = true,
  className = ''
}: TermHeaderProps) {
  
  const title = formatters.getDisplayTitle(term)

  return (
    <div className={`mb-8 ${className}`}>
      {/* Breadcrumb optimisé */}
      {showBreadcrumb && (
        <nav className="mb-4" aria-label="Fil d'Ariane">
          <ol className="flex items-center gap-2 text-sm text-neutral-600">
            <li>
              <Link href="/glossaire" className="hover:text-brand-600 transition-colors">
                Glossaire
              </Link>
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              {/* ✅ CORRIGÉ : Lien vers glossaire avec filtre catégorie */}
              <Link
                href={`/glossaire?category=${term.category.slug}`}
                className="hover:text-brand-600 transition-colors"
              >
                {term.category.name}
              </Link>
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <span className="text-neutral-800 font-medium">{title}</span>
            </li>
          </ol>
        </nav>
      )}
              
      {/* Titre principal */}
      <div className="space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-neutral-800 leading-tight">
          {title}
        </h1>
                
        {/* ✅ BADGES OPTIMISÉS : Sans couleur catégorie */}
        <div className="flex flex-wrap items-center gap-3">
          {/* ✅ CORRIGÉ : Catégorie sans couleur */}
          <Link
            href={`/glossaire?category=${term.category.slug}`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-full text-sm font-medium transition-colors"
          >
            📂 {term.category.name}
          </Link>
                    
          {/* Badge essentiel */}
          {term.is_essential && (
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">
              ⭐ Essentiel
            </span>
          )}
                    
          {/* ✅ CORRIGÉ : Difficulté avec la bonne fonction */}
          <span className="inline-flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-full text-sm font-medium">
            {formatters.formatDifficultyWithEmoji(term.difficulty_level)}
          </span>
        </div>
      </div>
    </div>
  )
}