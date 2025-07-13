// /var/www/megahub/websites/humari-site/src/app/api/builder/cache/flush/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const { paths, tags, all } = body
    
    console.log('🧹 Cache flush requested:', { paths, tags, all })
    
    const results: string[] = []
    
    // Revalider des paths spécifiques
    if (paths && Array.isArray(paths)) {
      for (const path of paths) {
        try {
          revalidatePath(path)
          results.push(`✅ Path revalidated: ${path}`)
          console.log(`✅ Revalidated path: ${path}`)
        } catch (error) {
          results.push(`❌ Failed to revalidate path ${path}: ${error}`)
          console.error(`❌ Failed to revalidate path ${path}:`, error)
        }
      }
    }
    
    // Revalider des tags spécifiques
    if (tags && Array.isArray(tags)) {
      for (const tag of tags) {
        try {
          revalidateTag(tag)
          results.push(`✅ Tag revalidated: ${tag}`)
          console.log(`✅ Revalidated tag: ${tag}`)
        } catch (error) {
          results.push(`❌ Failed to revalidate tag ${tag}: ${error}`)
          console.error(`❌ Failed to revalidate tag ${tag}:`, error)
        }
      }
    }
    
    // Flush global (paths principaux)
    if (all === true) {
      const commonPaths = [
        '/api/builder/registry',
        '/',
        '/about',
        '/services',
        '/contact'
      ]
      
      for (const path of commonPaths) {
        try {
          revalidatePath(path)
          results.push(`✅ Global revalidation: ${path}`)
        } catch (error) {
          results.push(`❌ Failed global revalidation ${path}: ${error}`)
        }
      }
    }
    
    return NextResponse.json({
      success: true,
      timestamp: new Date().toISOString(),
      cache_breaker: Date.now(),
      results
    }, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    })
    
  } catch (error) {
    console.error('❌ Cache flush error:', error)
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}