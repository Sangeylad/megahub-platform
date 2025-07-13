import { Metadata } from 'next'
import { Page } from '@/lib/types/api'  // ✅ Import direct au lieu de '@/lib/types'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://humari.fr'
const SITE_NAME = 'Humari'

export function generatePageMetadata(page: Page): Metadata {
  if (!page.content) {
    return {
      title: 'Page non trouvée',
      description: 'Cette page n\'existe pas'
    }
  }

  const { content } = page
  const canonicalUrl = `${SITE_URL}${page.url_path}`

  return {
    title: content.meta_title,
    description: content.meta_description,
    
    // Balises essentielles SEO
    alternates: {
      canonical: canonicalUrl
    },
    
    // Open Graph
    openGraph: {
      title: content.meta_title,
      description: content.meta_description,
      url: canonicalUrl,
      siteName: SITE_NAME,
      type: page.page_type === 'blog' ? 'article' : 'website',
      publishedTime: content.created_at,
      modifiedTime: content.updated_at,
    },
    
    // Twitter
    twitter: {
      card: 'summary_large_image',
      title: content.meta_title,
      description: content.meta_description,
    },
    
    // Données structurées JSON-LD
    other: {
      'application/ld+json': JSON.stringify(
        generateStructuredData(page)
      )
    }
  }
}

function generateStructuredData(page: Page) {
  const baseData = {
    '@context': 'https://schema.org',
    '@type': page.page_type === 'blog' ? 'Article' : 'WebPage',
    'name': page.content?.meta_title,
    'description': page.content?.meta_description,
    'url': `${SITE_URL}${page.url_path}`,
    'datePublished': page.content?.created_at,
    'dateModified': page.content?.updated_at,
    'publisher': {
      '@type': 'Organization',
      'name': SITE_NAME,
      'url': SITE_URL
    }
  }

  // Données spécifiques aux articles
  if (page.page_type === 'blog' && page.content) {
    return {
      ...baseData,
      '@type': 'Article',
      'headline': page.content.meta_title,
      'wordCount': page.content.word_count,
      'timeRequired': `PT${page.content.reading_time_minutes}M`,
      'author': {
        '@type': 'Organization',
        'name': SITE_NAME
      }
    }
  }

  return baseData
}

// Validation SEO
export function validateSEOContent(content: {
  meta_title: string
  meta_description: string
}): { isValid: boolean; warnings: string[] } {
  const warnings: string[] = []

  // Titre SEO
  if (content.meta_title.length > 60) {
    warnings.push('Le titre SEO dépasse 60 caractères')
  }
  if (content.meta_title.length < 30) {
    warnings.push('Le titre SEO est trop court (minimum 30 caractères)')
  }

  // Description SEO  
  if (content.meta_description.length > 160) {
    warnings.push('La description SEO dépasse 160 caractères')
  }
  if (content.meta_description.length < 120) {
    warnings.push('La description SEO est trop courte (minimum 120 caractères)')
  }

  return {
    isValid: warnings.length === 0,
    warnings
  }
}