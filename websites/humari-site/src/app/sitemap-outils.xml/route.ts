// app/sitemap-outils/route.ts
import { generateSitemapForType } from '@/lib/utils/sitemap'

export const dynamic = 'force-dynamic'

export async function GET() {
  console.log('🗺️ Sitemap outils route handler')
  return generateSitemapForType('outils')
}