// app/sitemap-blog/route.ts
import { generateSitemapForType } from '@/lib/utils/sitemap'

export const dynamic = 'force-dynamic'

export async function GET() {
  console.log('🗺️ Sitemap blog route handler')
  return generateSitemapForType('blog') // ✅ CHANGÉ de 'blog' vers 'blog'
}