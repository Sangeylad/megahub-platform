// app/[...slug]/page.tsx - VERSION CORRIGÉE

import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { renderAPI, HeaderConfigService } from '@/lib/api'
import { SectionRenderer } from '@/components/sections/SectionRenderer'
import { HeaderRenderer } from '@/components/layout/headers/HeaderRenderer'
import type { RenderResponse } from '@/lib/types/api'
import type { HeaderConfig } from '@/components/layout/headers/types'

interface PageProps {
  params: Promise<{ slug: string[] }>
}

interface KeywordData {
  keyword: string
  volume?: number
}

interface KeywordsStructure {
  primary?: KeywordData
  secondary?: KeywordData[]
}

export default async function DynamicPage({ params }: PageProps) {
  const { slug } = await params

  try {
    const pageData: RenderResponse | null = await renderAPI.getPageForRender(slug || [])
    
    if (!pageData) {
      notFound()
    }

    const { render_data, seo_metadata } = pageData
    const processedSections = render_data.sections || []
    
    // Générer la config header dynamique
    const websiteId = parseInt(process.env.MEGAHUB_WEBSITE_ID || '34')
    const dynamicHeaderConfig = await HeaderConfigService.generateDynamicHeaderConfig(websiteId)

    // Gestion header conditionnel
    const headerSection = processedSections.find(section => section.type === 'header')
    let showDefaultHeader = true
    let headerConfig = dynamicHeaderConfig

    if (headerSection) {
      if (headerSection.data?.variant === 'none') {
        showDefaultHeader = false
      } else {
        headerConfig = { 
          ...dynamicHeaderConfig, 
          ...headerSection.data 
        } as HeaderConfig
      }
    }

    const contentSections = processedSections.filter(section => section.type !== 'header')

    if (contentSections.length === 0) {
      return (
        <>
          {showDefaultHeader && <HeaderRenderer config={headerConfig} />}
          <main className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">
                {seo_metadata?.title || 'Page en construction'}
              </h1>
              <p className="text-gray-600">
                Cette page n&apos;a pas encore de contenu configuré.
              </p>
            </div>
          </main>
        </>
      )
    }

    return (
      <>
        {showDefaultHeader && <HeaderRenderer config={headerConfig} />}
        <main className="min-h-screen">
          {contentSections.map((section, index) => (
            <SectionRenderer 
              key={`${section.type}-${section.section_id || index}`} 
              section={section} 
            />
          ))}
        </main>
      </>
    )

  } catch (error) {
    console.error('Error rendering page:', error)
    notFound()
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params
  const urlPath = slug?.length > 0 ? `/${slug.join('/')}/` : '/'
  
  try {
    // Métadonnées spéciales pour les termes de glossaire
    if (urlPath.startsWith('/glossaire/definition-') && slug && slug.length >= 2) {
      const termSlug = slug[1]?.replace('definition-', '')
      
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/glossaire/terms/by-slug/${termSlug}?lang=fr`,
          { cache: 'force-cache' }
        )
        
        if (response.ok) {
          const term = await response.json()
          const title = term.current_translation?.title || termSlug
          const definition = term.current_translation?.definition || ''
          
          return {
            title: `${title} - Définition | Glossaire Marketing Digital`,
            description: definition.substring(0, 160),
            openGraph: {
              title: `${title} - Glossaire Marketing Digital`,
              description: definition.substring(0, 160),
              url: `https://humari.fr/glossaire/definition-${termSlug}/`,
              type: 'article'
            },
            twitter: {
              card: 'summary',
              title: `${title} - Glossaire Marketing Digital`,
              description: definition.substring(0, 160)
            }
          }
        }
      } catch (error) {
        console.error('Error fetching term metadata:', error)
      }
    }

    // Métadonnées standards depuis MEGAHUB
    const pageData = await renderAPI.getPageForRender(slug || [])
    
    if (!pageData?.seo_metadata) {
      return {
        title: 'Page non trouvée - Humari',
        description: 'Cette page n\'existe pas.'
      }
    }

    const { seo_metadata } = pageData
    const keywordsArray: string[] = []
    
    if (seo_metadata.keywords && typeof seo_metadata.keywords === 'object') {
      const keywords = seo_metadata.keywords as KeywordsStructure
      
      if (keywords.primary && 
          typeof keywords.primary === 'object' && 
          'keyword' in keywords.primary) {
        keywordsArray.push(keywords.primary.keyword)
      }
      
      if (keywords.secondary && Array.isArray(keywords.secondary)) {
        const secondaryKeywords = keywords.secondary
          .filter((k: unknown): k is KeywordData => 
            k !== null && 
            typeof k === 'object' && 
            'keyword' in k
          )
          .map((k: KeywordData) => k.keyword)
        
        keywordsArray.push(...secondaryKeywords)
      }
    }
    
    return {
      title: seo_metadata.title || 'Humari - Agence Marketing Digital',
      description: seo_metadata.description || 'Experts en SEO et Growth Hacking',
      openGraph: {
        title: seo_metadata.title || 'Humari',
        description: seo_metadata.description || 'Experts en SEO et Growth Hacking',
        url: `https://humari.fr${urlPath}`,
        siteName: 'Humari',
        type: 'website',
        images: seo_metadata.featured_image ? [seo_metadata.featured_image] : undefined
      },
      twitter: {
        card: 'summary_large_image',
        title: seo_metadata.title || 'Humari',
        description: seo_metadata.description || 'Experts en SEO et Growth Hacking'
      },
      alternates: {
        canonical: seo_metadata.canonical || `https://humari.fr${urlPath}`
      },
      keywords: keywordsArray.length > 0 ? keywordsArray : undefined
    }
  } catch (error) {
    console.error('Metadata generation error:', error)
    return {
      title: 'Humari - Agence Marketing Digital',
      description: 'Experts en SEO et Growth Hacking'
    }
  }
}