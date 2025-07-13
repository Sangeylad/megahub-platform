// app/api/sitemap/route.ts - VERSION CORRIGÉE AVEC GLOSSAIRE
import { NextResponse } from 'next/server'
import { renderAPI } from '@/lib/api'
import type { SitemapTypeResponse, SitemapType } from '@/lib/types/api'

export const dynamic = 'force-dynamic'

const VALID_SITEMAP_TYPES: readonly SitemapType[] = ['index', 'vitrine', 'blog', 'outils', 'glossaire'] as const // ← AJOUT 'glossaire'
const VALID_DEBUG_ACTIONS = ['debug', 'stats'] as const
type DebugAction = typeof VALID_DEBUG_ACTIONS[number]

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const typeParam = searchParams.get('type') || 'vitrine'
  
  console.log(`🗺️ API Sitemap called with type: ${typeParam}`)
  
  try {
    // Validation du type
    if (!VALID_SITEMAP_TYPES.includes(typeParam as SitemapType)) {
      return NextResponse.json(
        {
          error: 'Type de sitemap invalide',
          provided: typeParam,
          available_types: VALID_SITEMAP_TYPES
        },
        { status: 400 }
      )
    }
    
    const type: SitemapType = typeParam as SitemapType
    
    // 🎯 CAS INDEX EN PREMIER
    if (type === 'index') {
      const indexData = await renderAPI.getSitemapIndex()
      return NextResponse.json(indexData, {
        headers: {
          'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=7200'
        }
      })
    }
    
    // 🔧 CORRECTION : Utiliser getSitemapForType() au lieu des méthodes inexistantes
    const data: SitemapTypeResponse = await renderAPI.getSitemapForType(type)
    
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=7200',
        'X-Sitemap-Type': type,
        'X-Pages-Count': data.total.toString()
      }
    })
   
  } catch (error) {
    console.error(`❌ API Sitemap ${typeParam} error:`, error)
    
    const fallbackType = VALID_SITEMAP_TYPES.includes(typeParam as SitemapType)
      ? (typeParam as SitemapType)
      : 'vitrine'
    
    const fallbackData: SitemapTypeResponse = {
      pages: [],
      total: 0,
      type: fallbackType,
      type_name: `Sitemap ${fallbackType}`,
      generated_at: new Date().toISOString()
    }
    
    return NextResponse.json(
      {
        error: 'Erreur récupération sitemap',
        fallback_data: fallbackData
      },
      {
        status: 500,
        headers: {
          'X-Error': 'sitemap-generation-failed'
        }
      }
    )
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { action } = body
    
    if (!VALID_DEBUG_ACTIONS.includes(action)) {
      return NextResponse.json(
        {
          error: 'Action non supportée',
          provided: action,
          available_actions: VALID_DEBUG_ACTIONS
        },
        { status: 400 }
      )
    }
    
    const validAction = action as DebugAction
    
    if (validAction === 'debug') {
      console.log('🔍 Sitemap debug requested')
      const debugData = await renderAPI.getSitemapDebug()
      const stats = await renderAPI.getSitemapStats()
      
      return NextResponse.json({
        debug: debugData,
        stats
      })
    }
    
    if (validAction === 'stats') {
      const statsData = await renderAPI.getSitemapStats()
      return NextResponse.json(statsData)
    }
    
    return NextResponse.json(
      { error: 'Action non traitée' },
      { status: 500 }
    )
    
  } catch (error) {
    console.error('❌ Sitemap POST error:', error)
    return NextResponse.json(
      { error: 'Erreur traitement requête' },
      { status: 500 }
    )
  }
}