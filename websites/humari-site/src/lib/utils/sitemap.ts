// lib/utils/sitemap.ts - VERSION CORRIGÉE SANS INVENTION
import { NextResponse } from 'next/server'
import { renderAPI } from '@/lib/api'
import type { SitemapTypeResponse } from '@/lib/types/api'

// ✅ TYPES BASÉS SUR LA VRAIE RÉPONSE BACKEND BLOG
interface BlogSitemapCategory {
  url: string
  lastmod: string
  changefreq?: string
  priority?: string | number
  title: string
  page_type: string
}

interface BlogSitemapArticle {
  url: string
  lastmod: string
  changefreq?: string
  priority?: string | number
  title: string
  page_type: string
}

interface BlogCategoryData {
  category: BlogSitemapCategory
  articles: BlogSitemapArticle[]
  articles_count: number
}

interface BlogSitemapResponse {
  categories?: BlogCategoryData[]
  orphan_articles?: BlogSitemapArticle[]
  total_categories: number
  total_articles: number
  total_orphan_articles: number
  type: string
  type_name: string
  generated_at: string
}

export async function generateSitemapForType(
  type: 'vitrine' | 'blog' | 'outils' | 'glossaire'
): Promise<NextResponse> {
  try {
    console.log(`🗺️ Generating XML sitemap for type: ${type}`)
    
    const data = await renderAPI.getSitemapForType(type)
    
    // ✅ GESTION SPÉCIALE POUR LE BLOG HIÉRARCHIQUE
    const sitemap = type === 'blog' 
      ? generateBlogSitemapXML(data as unknown as BlogSitemapResponse) 
      : generateStandardSitemapXML(data)
    
    return new NextResponse(sitemap, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml',
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=7200'
      }
    })
    
  } catch (error) {
    console.error(`❌ Sitemap XML ${type} error:`, error)
    return generateEmptySitemap()
  }
}

// ✅ FONCTION POUR BLOG HIÉRARCHIQUE (STRUCTURE BACKEND RÉELLE)
function generateBlogSitemapXML(data: BlogSitemapResponse): string {
  const baseUrl = `https://${process.env.NEXT_PUBLIC_DOMAIN}`
  
  let sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`

  // 1. Ajouter les catégories
  if (data.categories && Array.isArray(data.categories)) {
    data.categories.forEach((categoryData: BlogCategoryData) => {
      const category = categoryData.category
      if (category?.url) {
        const fullUrl = category.url.startsWith('http') 
          ? category.url 
          : `${baseUrl}${category.url.startsWith('/') ? category.url : '/' + category.url}`
        
        sitemap += `
  <url>
    <loc>${fullUrl}</loc>
    <lastmod>${category.lastmod}</lastmod>
    <changefreq>${category.changefreq || 'weekly'}</changefreq>
    <priority>${category.priority || '0.8'}</priority>
  </url>`
      }
      
      // 2. Ajouter les articles de cette catégorie
      if (categoryData.articles && Array.isArray(categoryData.articles)) {
        categoryData.articles.forEach((article: BlogSitemapArticle) => {
          if (article?.url) {
            const fullUrl = article.url.startsWith('http') 
              ? article.url 
              : `${baseUrl}${article.url.startsWith('/') ? article.url : '/' + article.url}`
            
            sitemap += `
  <url>
    <loc>${fullUrl}</loc>
    <lastmod>${article.lastmod}</lastmod>
    <changefreq>${article.changefreq || 'weekly'}</changefreq>
    <priority>${article.priority || '0.6'}</priority>
  </url>`
          }
        })
      }
    })
  }
  
  // 3. Ajouter les articles orphelins
  if (data.orphan_articles && Array.isArray(data.orphan_articles)) {
    data.orphan_articles.forEach((article: BlogSitemapArticle) => {
      if (article?.url) {
        const fullUrl = article.url.startsWith('http') 
          ? article.url 
          : `${baseUrl}${article.url.startsWith('/') ? article.url : '/' + article.url}`
        
        sitemap += `
  <url>
    <loc>${fullUrl}</loc>
    <lastmod>${article.lastmod}</lastmod>
    <changefreq>${article.changefreq || 'weekly'}</changefreq>
    <priority>${article.priority || '0.6'}</priority>
  </url>`
      }
    })
  }

  sitemap += `
</urlset>`

  return sitemap
}

// ✅ FONCTION STANDARD POUR LES AUTRES TYPES (vitrine, outils, glossaire)
function generateStandardSitemapXML(data: SitemapTypeResponse): string {
  const baseUrl = `https://${process.env.NEXT_PUBLIC_DOMAIN}`
  
  let sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`

  // Structure standard avec data.pages
  if (data.pages && Array.isArray(data.pages)) {
    data.pages.forEach((page) => {
      const fullUrl = page.url.startsWith('http') 
        ? page.url 
        : `${baseUrl}${page.url.startsWith('/') ? page.url : '/' + page.url}`
      
      sitemap += `
  <url>
    <loc>${fullUrl}</loc>
    <lastmod>${page.lastmod}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`
    })
  }

  sitemap += `
</urlset>`

  return sitemap
}

function generateEmptySitemap(): NextResponse {
  const baseUrl = `https://${process.env.NEXT_PUBLIC_DOMAIN}`
  const currentDate = new Date().toISOString()
  
  const emptySitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${baseUrl}/</loc>
    <lastmod>${currentDate}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>`
  
  return new NextResponse(emptySitemap, {
    status: 200,
    headers: { 'Content-Type': 'application/xml' }
  })
}