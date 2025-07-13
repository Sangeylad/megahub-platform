// /var/www/megahub/websites/humari-site/src/app/api/builder/registry/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { SectionsRegistry } from '@/lib/sections-registry'

export async function GET(request: NextRequest) {
  try {
    console.log('📋 Registry API called - Starting debug...')
    
    // 🧪 TEST DIRECT : Importer le schema manuellement
    console.log('📋 Testing direct import...')
    try {
      const { statsSchema } = await import('@/lib/sections-registry/schemas/stats-section.schema')
      console.log('📋 Direct import SUCCESS - statsSchema:', !!statsSchema)
      console.log('📋 Direct import props:', Object.keys(statsSchema.props))
      console.log('📋 Has stats prop:', 'stats' in statsSchema.props)
    } catch (importError) {
      console.error('📋 Direct import FAILED:', importError)
    }
    
    // 🧪 TEST REGISTRY
    const sections = SectionsRegistry.getAllSections()
    const statsSection = sections.find(s => s.type === 'stats_section')
    
    console.log(`📋 Registry returned ${sections.length} sections`)
    console.log('📋 Stats section found:', !!statsSection)
    
    if (statsSection) {
      console.log('📋 Stats section props:', Object.keys(statsSection.props))
      console.log('📋 Has stats prop in registry:', 'stats' in statsSection.props)
    }
    
    const cacheBreaker = Date.now()
    const categories = [...new Set(sections.map(s => s.category))]
    
    const response = {
      success: true,
      timestamp: new Date().toISOString(),
      cache_breaker: cacheBreaker,
      website_info: {
        domain: request.headers.get('host') ?? 'unknown',
        user_agent: request.headers.get('user-agent') ?? 'unknown'
      },
      sections,
      metadata: {
        total_sections: sections.length,
        layout_containers: sections.filter(s => s.layoutContainer === true).length,
        content_sections: sections.filter(s => s.layoutContainer !== true).length,
        categories
      }
    }
    
    return NextResponse.json(response, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
        'Pragma': 'no-cache',
        'Expires': '0',
        'X-Cache-Breaker': cacheBreaker.toString(),
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    })
    
  } catch (error) {
    console.error('❌ Registry API Error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}