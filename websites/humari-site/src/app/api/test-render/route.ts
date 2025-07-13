// src/app/api/test-render/route.ts - ROUTE DEBUG
import { renderAPI } from '@/lib/api'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const path = searchParams.get('path') || '/marketing'
  
  console.log(`🧪 [TEST-RENDER] Testing path: ${path}`)
  
  // Variables d'env
  console.log('🔧 Environment:', {
    MEGAHUB_API_URL: process.env.MEGAHUB_API_URL,
    MEGAHUB_WEBSITE_ID: process.env.MEGAHUB_WEBSITE_ID,
    NODE_ENV: process.env.NODE_ENV
  })
  
  try {
    const slugArray = path === '/' ? [] : path.split('/').filter(Boolean)
    console.log('📤 Calling renderAPI.getPageForRender with:', slugArray)
    
    const data = await renderAPI.getPageForRender(slugArray)
    
    console.log('📥 API Response:', {
      hasData: !!data,
      dataPreview: data ? {
        id: data.id,
        title: data.title,
        url_path: data.url_path,
        sectionsCount: data.render_data?.sections?.length
      } : null
    })
    
    return NextResponse.json({
      success: true,
      path,
      slugArray,
      hasData: !!data,
      environment: {
        MEGAHUB_API_URL: process.env.MEGAHUB_API_URL,
        MEGAHUB_WEBSITE_ID: process.env.MEGAHUB_WEBSITE_ID
      },
      data: data ? {
        id: data.id,
        title: data.title,
        url_path: data.url_path,
        sectionsCount: data.render_data?.sections?.length,
        strategy: data.render_data?.strategy
      } : null
    })
  } catch (error) {
    console.error('❌ [TEST-RENDER] Error:', error)
    return NextResponse.json({
      success: false,
      path,
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    }, { status: 500 })
  }
}