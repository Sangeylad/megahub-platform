// app/sitemap-vitrine/route.ts
import { generateSitemapForType } from '@/lib/utils/sitemap'

export const dynamic = 'force-dynamic'

export async function GET() {
  console.log('🗺️ Sitemap vitrine route handler')
  return generateSitemapForType('vitrine')
}