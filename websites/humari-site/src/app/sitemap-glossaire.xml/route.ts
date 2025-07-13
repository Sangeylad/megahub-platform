// app/sitemap-glossaire/route.ts
import { generateSitemapForType } from '@/lib/utils/sitemap'

export const dynamic = 'force-dynamic'

export async function GET() {
  console.log('🗺️ Sitemap glossaire route handler')
  return generateSitemapForType('glossaire')
}