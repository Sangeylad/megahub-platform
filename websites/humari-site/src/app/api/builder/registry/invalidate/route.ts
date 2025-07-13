// /var/www/megahub/websites/humari-site/src/app/api/builder/registry/invalidate/route.ts
import { NextRequest, NextResponse } from 'next/server'

interface InvalidateRequest {
  website_id?: number
  reason?: string
  preload?: boolean
  force_restart?: boolean
}

export async function POST(request: NextRequest) {
  try {
    console.log('🔄 Registry invalidation endpoint called')
    
    // ← FIX : Lire le body UNE SEULE FOIS
    let requestData: InvalidateRequest = {}
    
    try {
      // Clone la request pour éviter le problème "body unusable"
      const clonedRequest = request.clone()
      const contentType = clonedRequest.headers.get('content-type')
      
      if (contentType?.includes('application/json')) {
        const bodyText = await clonedRequest.text()
        if (bodyText.trim()) {
          requestData = JSON.parse(bodyText)
          console.log('📦 Parsed request data:', requestData)
        }
      }
    } catch (parseError) {
      console.warn('⚠️ Could not parse request body:', parseError)
      // Continue avec les defaults
    }
    
    const DJANGO_API = process.env.DJANGO_API_URL || 'https://backoffice.humari.fr'
    const WEBHOOK_SECRET = process.env.REGISTRY_WEBHOOK_SECRET
    
    if (!WEBHOOK_SECRET) {
      console.error('❌ REGISTRY_WEBHOOK_SECRET not configured')
      return NextResponse.json({
        success: false,
        error: 'Webhook secret not configured'
      }, { status: 500 })
    }
    
    const cacheBreaker = Date.now()
    
    const payload = {
      website_id: requestData.website_id || 34,
      event: 'registry_updated',
      timestamp: new Date().toISOString(),
      reason: requestData.reason || 'Next.js registry updated',
      preload: requestData.preload || false,
      cache_breaker: cacheBreaker,
      force_restart: requestData.force_restart || false
    }
    
    console.log('🔄 Sending webhook to Django:', `${DJANGO_API}/api/seo/website-registries/webhook/invalidate/`)
    console.log('📦 Payload:', payload)
    
    try {
      // ← Créer une nouvelle requête fetch (pas de réutilisation du body)
      const webhookResponse = await fetch(`${DJANGO_API}/api/seo/website-registries/webhook/invalidate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${WEBHOOK_SECRET}`,
          'X-Registry-Source': 'nextjs-invalidate',
          'X-Cache-Breaker': cacheBreaker.toString(),
          'User-Agent': 'NextJS-Registry-Invalidator/1.0'
        },
        body: JSON.stringify(payload), // ← Nouveau payload, pas réutilisation
        signal: AbortSignal.timeout(15000) // ← Augmenter timeout
      })
      
      console.log('📡 Django webhook response status:', webhookResponse.status)
      
      let djangoResponse = null
      try {
        const responseText = await webhookResponse.text()
        
        if (responseText.trim()) {
          try {
            djangoResponse = JSON.parse(responseText)
            console.log('📦 Django response (JSON):', djangoResponse)
          } catch {
            console.log('📄 Django response (text):', responseText.substring(0, 200))
            djangoResponse = { raw_response: responseText.substring(0, 200) }
          }
        } else {
          console.log('📄 Django response empty')
          djangoResponse = { empty_response: true }
        }
      } catch (responseError) {
        console.warn('⚠️ Error reading Django response:', responseError)
        djangoResponse = { error: 'Could not read response' }
      }
      
      const result = {
        success: true,
        webhook_sent: webhookResponse.ok,
        django_status: webhookResponse.status,
        django_response: djangoResponse,
        payload_sent: payload,
        cache_breaker: cacheBreaker,
        timestamp: new Date().toISOString()
      }
      
      if (webhookResponse.ok) {
        console.log('✅ Webhook sent successfully')
      } else {
        console.error('❌ Webhook failed with status:', webhookResponse.status)
      }
      
      return NextResponse.json(result, {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'X-Cache-Breaker': cacheBreaker.toString()
        }
      })
      
    } catch (fetchError) {
      console.error('❌ Network error calling Django:', fetchError)
      
      return NextResponse.json({
        success: false,
        error: `Network error: ${fetchError instanceof Error ? fetchError.message : String(fetchError)}`,
        webhook_details: {
          url: `${DJANGO_API}/api/seo/website-registries/webhook/invalidate/`,
          has_secret: !!WEBHOOK_SECRET
        },
        cache_breaker: cacheBreaker,
        timestamp: new Date().toISOString()
      }, { status: 500 })
    }
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    const errorStack = error instanceof Error ? error.stack : undefined
    
    console.error('❌ General webhook error:', errorMessage)
    if (errorStack) {
      console.error('Stack trace:', errorStack)
    }
    
    return NextResponse.json({
      success: false,
      error: errorMessage,
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}

// GET pour debug
export async function GET() {
  const DJANGO_API = process.env.DJANGO_API_URL
  const hasSecret = !!process.env.REGISTRY_WEBHOOK_SECRET
  
  return NextResponse.json({
    configured: hasSecret,
    django_api: DJANGO_API,
    webhook_url: `${DJANGO_API}/api/seo/website-registries/webhook/invalidate/`,
    timestamp: new Date().toISOString(),
    cache_breaker: Date.now()
  }, {
    headers: {
      'Cache-Control': 'no-cache'
    }
  })
}