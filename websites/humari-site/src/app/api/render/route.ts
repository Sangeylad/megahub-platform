// app/api/render/route.ts
import { NextRequest, NextResponse } from 'next/server'

const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL!
const MEGAHUB_WEBSITE_ID = process.env.MEGAHUB_WEBSITE_ID!

export async function GET() {
  return NextResponse.json({ message: 'Route handler API fonctionne!' })
}

export async function POST(request: NextRequest) {
  console.log('🎯 Route handler API /render appelé!')
  
  try {
    const body = await request.json()
    console.log('📥 Body reçu:', body)
    
    // Validation basique
    if (!body.url_path || !body.website_id) {
      console.error('❌ Validation échouée:', body)
      return NextResponse.json(
        { error: 'url_path et website_id requis' },
        { status: 400 }
      )
    }

    const requestBody = {
      ...body,
      website_id: parseInt(MEGAHUB_WEBSITE_ID)
    }

    console.log('🌐 Appel vers MEGAHUB:', `${MEGAHUB_API_URL}/seo/render/by_slug/`)

    const response = await fetch(`${MEGAHUB_API_URL}/seo/render/by_slug/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      cache: 'no-store'
    })

    console.log('📡 MEGAHUB Response:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ MEGAHUB Error:', errorText)
      return NextResponse.json(
        { error: 'Erreur backend', details: errorText },
        { status: response.status }
      )
    }

    const data = await response.json()
    console.log('✅ Données OK, retour vers client')
    
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=7200'
      }
    })

  } catch (error) {
    console.error('💥 Erreur route handler:', error)
    return NextResponse.json(
      { error: 'Erreur serveur', details: error instanceof Error ? error.message : 'Erreur inconnue' },
      { status: 500 }
    )
  }
}