// /var/www/megahub/websites/humari-site/src/components/sections/GlossaryTermSection.tsx
'use client'

import React, { useEffect } from 'react'
import { TermDisplay } from '@/components/tools/glossary-search'
import type { SectionComponentProps } from '@/lib/types/sections'

interface GlossaryTermData {
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

interface GlossaryTermSectionProps {
  // ✅ DONNÉES INJECTÉES PAR LE BACKEND (priorité)
  term?: GlossaryTermData
  
  // ✅ FALLBACK : slug pour cas où term absent
  slug?: string
  
  // Configuration section
  language?: string
  showRelated?: boolean
  showBreadcrumb?: boolean
  showMetadata?: boolean
  hideNavigation?: boolean
  customTitle?: string
  background?: 'transparent' | 'white' | 'neutral' | 'gradient'
  padding?: 'none' | 'small' | 'normal' | 'large'
  maxWidth?: '3xl' | '4xl' | '5xl' | '6xl' | 'full'
  relatedLimit?: number
  cta_text?: string
  cta_url?: string
  cta_variant?: 'primary' | 'secondary' | 'outline'
  customCSS?: string
  tracking_event?: string
  tracking_category?: string
  tracking_params?: string
}

declare global {
  interface Window {
    gtag?: (command: string, targetId: string, config?: Record<string, unknown>) => void
  }
}

export function GlossaryTermSection({ data }: SectionComponentProps<GlossaryTermSectionProps>) {
  const {
    term, // ✅ PRIORITÉ AUX DONNÉES INJECTÉES
    slug,  // ✅ FALLBACK
    language = 'fr',
    showRelated = true,
    showBreadcrumb = true,
    hideNavigation = false,
    customTitle,
    background = 'white',
    padding = 'normal',
    maxWidth = '4xl',
    relatedLimit = 5, // ✅ VALEUR PAR DÉFAUT
    cta_text,
    cta_url,
    cta_variant = 'primary',
    customCSS,
    tracking_event,
    tracking_category = 'Glossaire',
    tracking_params
  } = data
  
  // ✅ TRACKING
  useEffect(() => {
    const termSlug = term?.slug || slug
    if (tracking_event && termSlug) {
      let trackingData = {}
      if (tracking_params) {
        try {
          trackingData = JSON.parse(tracking_params)
        } catch {
          console.warn('Invalid tracking params JSON:', tracking_params)
        }
      }
      
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', tracking_event, {
          event_category: tracking_category,
          event_label: termSlug,
          ...trackingData
        })
      }
    }
  }, [term?.slug, slug, tracking_event, tracking_category, tracking_params])

  const getSectionClasses = () => {
    const backgrounds = {
      'transparent': 'bg-transparent',
      'white': 'bg-white',
      'neutral': 'bg-neutral-50',
      'gradient': 'bg-gradient-to-br from-brand-50 to-blue-50'
    }
    
    const paddings = {
      'none': 'py-0 px-0',
      'small': 'py-6 px-4',
      'normal': 'py-12 px-6',
      'large': 'py-16 px-8'
    }

    return `${backgrounds[background]} ${paddings[padding]} relative`
  }

  const getContainerClasses = () => {
    const containers = {
      '3xl': 'max-w-3xl',
      '4xl': 'max-w-4xl',
      '5xl': 'max-w-5xl',
      '6xl': 'max-w-6xl',
      'full': 'max-w-full'
    }
    return `${containers[maxWidth]} mx-auto`
  }

  const getCtaClasses = () => {
    const variants = {
      'primary': 'bg-brand-600 hover:bg-brand-700 text-white',
      'secondary': 'bg-neutral-100 hover:bg-neutral-200 text-neutral-700',
      'outline': 'border border-brand-600 text-brand-600 hover:bg-brand-50'
    }
    return `inline-flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${variants[cta_variant]}`
  }

  // ✅ VÉRIFICATION DES DONNÉES
  const termSlug = term?.slug || slug
  if (!termSlug && !term) {
    return (
      <section className={getSectionClasses()}>
        <div className={getContainerClasses()}>
          <div className="text-center py-12">
            <div className="text-red-600 font-medium">
              ⚠️ Erreur : données du terme manquantes
            </div>
            <p className="text-neutral-600 mt-2">
              Aucune donnée de terme disponible (ni term, ni slug).
            </p>
          </div>
        </div>
      </section>
    )
  }

  console.log('📖 GlossaryTermSection - Mode:', term ? 'Données injectées' : 'Fetch par slug')
  console.log('📖 Term data:', term ? 'Disponible' : 'Absent')
  console.log('📖 Slug fallback:', termSlug)

  return (
    <section 
      className={getSectionClasses()}
      data-section="glossary-term"
      data-tracking-id={tracking_event}
    >
      {customCSS && (
        <style dangerouslySetInnerHTML={{ __html: customCSS }} />
      )}
      
      <div className={getContainerClasses()}>
        {customTitle && (
          <header className="text-center mb-8">
            <h1 className="text-3xl font-bold text-neutral-800">
              {customTitle}
            </h1>
          </header>
        )}
        
        {/* ✅ NOUVEAU : Mode hybride avec données injectées OU fetch */}
        <TermDisplay
          // ✅ CORRECTION : Gestion explicite du type undefined
          termData={term ? term : undefined}
          
          // ✅ CORRECTION : Pas de slug si term existe
          slug={!term ? termSlug : undefined}
          
          language={language}
          showRelated={showRelated}
          showBreadcrumb={showBreadcrumb && !hideNavigation}
          relatedLimit={relatedLimit}
        />
        
        {cta_text && cta_url && (
          <div className="mt-8 text-center">
            <a href={cta_url} className={getCtaClasses()}>
              {cta_text}
            </a>
          </div>
        )}
      </div>
    </section>
  )
}