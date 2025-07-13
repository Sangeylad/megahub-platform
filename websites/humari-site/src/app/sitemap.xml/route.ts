// app/sitemap.xml/route.ts
import { NextResponse } from 'next/server'
import { renderAPI } from '@/lib/api'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    console.log('🗺️ Sitemap index route handler')
    
    const indexData = await renderAPI.getSitemapIndex()
    const baseUrl = `https://${process.env.NEXT_PUBLIC_DOMAIN}`
    
    let sitemapIndex = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`

    indexData.sitemaps.forEach(sitemap => {
      sitemapIndex += `
  <sitemap>
    <loc>${baseUrl}/sitemap-${sitemap.type}.xml</loc>
    <lastmod>${sitemap.lastmod}</lastmod>
  </sitemap>`
    })

    sitemapIndex += `
</sitemapindex>`

    return new NextResponse(sitemapIndex, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml',
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=7200'
      }
    })
    
  } catch (error) {
    console.error('❌ Sitemap index error:', error)
    
    const fallbackIndex = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://${process.env.NEXT_PUBLIC_DOMAIN}/sitemap-vitrine.xml</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
  </sitemap>
</sitemapindex>`
    
    return new NextResponse(fallbackIndex, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml',
        'X-Error': 'sitemap-index-fallback'
      }
    })
  }
}